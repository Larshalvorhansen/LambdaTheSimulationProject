// tiny_rack.c
// A tiny, educational modular-synth engine inspired by VCV Rack.
// Written in C, single-file, PortAudio backend. Public domain / MIT-ISH, do
// what you want. Build: see Makefile (uses pkg-config for portaudio-2.0) Run:
// ./tiny_rack -d 6   (plays a short demo patch for 6 seconds)

#include <math.h>
#include <portaudio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ----------------------- Engine limits/tuning -----------------------
#define MAX_MODULES 64
#define MAX_INPUTS 8
#define MAX_OUTPUTS 8
#define MAX_WIRES 128

// Single connection per input (simplifies), like a hard-normalled jack.
// If you need summing, add an explicit MIX module in your patch.

// ----------------------- Module types ------------------------------
typedef enum {
  MOD_PARAM, // constant CV output (value)
  MOD_GATE,  // gate high for N seconds, then low
  MOD_VCO,   // sine VCO (Hz control)
  MOD_LFO,   // sine LFO (Hz)
  MOD_ADSR,  // envelope generator (gate in -> env out)
  MOD_VCA,   // VCA (sig in * gain)
  MOD_MIX4,  // 4-channel mixer
  MOD_OUT    // sink: L/R inputs to audio interface
} ModuleType;

// Forward decl
struct Module;

typedef struct Wire {
  int from_module; // module index
  int from_port;   // output port idx
  int to_module;   // module index
  int to_port;     // input port idx
} Wire;

typedef struct Module {
  ModuleType type;
  char name[32];
  int id;
  int num_inputs;
  int num_outputs;

  // Per-input connection mapping (single source per input)
  int in_src_mod[MAX_INPUTS];
  int in_src_port[MAX_INPUTS];

  // Per-sample state
  union {
    struct {
      float value;
    } param; // MOD_PARAM
    struct {
      float length_s;
      float t;
    } gate; // MOD_GATE
    struct {
      float phase;
      float freq;
    } vco; // MOD_VCO (freq param if no CV)
    struct {
      float phase;
      float freq;
    } lfo; // MOD_LFO
    struct {
      float a, d, s, r; // seconds, sustain [0..1]
      float env;        // current value [0..1]
      int state;        // 0=idle,1=att,2=dec,3=sus,4=rel
    } adsr;
    struct {
      float gain;
    } vca;
    struct {
      float gains[4];
    } mix4;
    struct { /* sink: no state */
    } out;
  } u;
} Module;

// The rack/graph
typedef struct Rack {
  int sample_rate;
  int block_size; // not used heavily; we go sample-by-sample inside the
                  // callback

  int num_modules;
  Module modules[MAX_MODULES];

  int num_wires;
  Wire wires[MAX_WIRES];

  int topo_order[MAX_MODULES];
  int topo_count;

  // Runtime out sink
  int out_module; // index of MOD_OUT (we support exactly one)
} Rack;

// ----------------------- Helpers -----------------------------------
static float clampf(float x, float lo, float hi) {
  return x < lo ? lo : (x > hi ? hi : x);
}

static void module_init(Module *m, ModuleType t, const char *name, int id,
                        int n_in, int n_out) {
  memset(m, 0, sizeof(*m));
  m->type = t;
  snprintf(m->name, sizeof(m->name), "%s", name ? name : "");
  m->id = id;
  m->num_inputs = n_in;
  m->num_outputs = n_out;
  for (int i = 0; i < MAX_INPUTS; i++) {
    m->in_src_mod[i] = -1;
    m->in_src_port[i] = -1;
  }
}

static int rack_add_module(Rack *r, ModuleType t, const char *name, int n_in,
                           int n_out) {
  if (r->num_modules >= MAX_MODULES)
    return -1;
  int id = r->num_modules;
  module_init(&r->modules[id], t, name, id, n_in, n_out);
  if (t == MOD_OUT)
    r->out_module = id;
  r->num_modules++;
  return id;
}

static bool rack_connect(Rack *r, int from_m, int from_p, int to_m, int to_p) {
  if (r->num_wires >= MAX_WIRES)
    return false;
  if (to_p >= r->modules[to_m].num_inputs)
    return false;
  r->wires[r->num_wires++] = (Wire){from_m, from_p, to_m, to_p};
  // Install single-source mapping
  r->modules[to_m].in_src_mod[to_p] = from_m;
  r->modules[to_m].in_src_port[to_p] = from_p;
  return true;
}

// Build a topological order over modules (by module-level deps, not port level)
static void rack_build_topo(Rack *r) {
  int indeg[MAX_MODULES] = {0};
  for (int i = 0; i < r->num_wires; i++) {
    Wire w = r->wires[i];
    if (w.from_module != w.to_module)
      indeg[w.to_module]++;
  }
  int q[MAX_MODULES];
  int qh = 0, qt = 0;
  for (int m = 0; m < r->num_modules; m++)
    if (indeg[m] == 0)
      q[qt++] = m;
  r->topo_count = 0;
  while (qh < qt) {
    int m = q[qh++];
    r->topo_order[r->topo_count++] = m;
    for (int i = 0; i < r->num_wires; i++) {
      Wire w = r->wires[i];
      if (w.from_module == m && w.from_module != w.to_module) {
        if (--indeg[w.to_module] == 0)
          q[qt++] = w.to_module;
      }
    }
  }
  // If cycle, just fall back to linear order (naive)
  if (r->topo_count != r->num_modules) {
    fprintf(stderr,
            "[warn] cycle or disconnected graph; using linear order.\n");
    r->topo_count = r->num_modules;
    for (int m = 0; m < r->num_modules; m++)
      r->topo_order[m] = m;
  }
}

// Fetch single-source input or 0.0
static inline float in_val(const Rack *r, Module *m, int in_port,
                           float (*outvals)[MAX_OUTPUTS]) {
  if (in_port >= m->num_inputs)
    return 0.f;
  int sm = m->in_src_mod[in_port];
  int sp = m->in_src_port[in_port];
  if (sm < 0 || sp < 0)
    return 0.f;
  return outvals[sm][sp];
}

// ----------------------- Module DSP --------------------------------
static inline float tick_param(Module *m) {
  return m->u.param.value; // constant
}

static inline float tick_gate(Module *m, float dt) {
  // High for length_s, then low
  float v = (m->u.gate.t < m->u.gate.length_s) ? 1.f : 0.f;
  m->u.gate.t += dt;
  return v;
}

static inline float tick_sine_osc(Module *m, float freq, float sr) {
  if (freq < 0.f)
    freq = 0.f;
  float inc = (float)(2.0 * M_PI) * freq / sr;
  m->u.vco.phase += inc;
  if (m->u.vco.phase > (float)(2.0 * M_PI))
    m->u.vco.phase -= (float)(2.0 * M_PI);
  return sinf(m->u.vco.phase);
}

static inline float tick_vco(Module *m, float sr, float cv_hz) {
  float f = m->u.vco.freq + cv_hz; // cv adds in Hz domain (simple)
  return tick_sine_osc(m, f, sr);
}

static inline float tick_lfo(Module *m, float sr) {
  return tick_sine_osc(m, m->u.lfo.freq, sr);
}

static inline float tick_adsr(Module *m, float gate, float sr) {
  // Simple linear ADSR
  float a = fmaxf(1e-5f, m->u.adsr.a);
  float d = fmaxf(1e-5f, m->u.adsr.d);
  float s = clampf(m->u.adsr.s, 0.f, 1.f);
  float r = fmaxf(1e-5f, m->u.adsr.r);
  float env = m->u.adsr.env;
  if (gate >= 0.5f) {
    if (m->u.adsr.state == 0 ||
        m->u.adsr.state == 4) { // idle->attack, release->attack
      m->u.adsr.state = 1;
    }
    if (m->u.adsr.state == 1) { // attack to 1.0
      float step = 1.f / (a * sr);
      env += step;
      if (env >= 1.f) {
        env = 1.f;
        m->u.adsr.state = 2;
      }
    } else if (m->u.adsr.state == 2) { // decay to s
      float step = 1.f / (d * sr);
      if (env > s) {
        env -= step;
        if (env <= s) {
          env = s;
          m->u.adsr.state = 3;
        }
      } else {
        env = s;
        m->u.adsr.state = 3;
      }
    } else if (m->u.adsr.state == 3) { // sustain
      env = s;
    }
  } else {
    if (m->u.adsr.state != 0) {
      m->u.adsr.state = 4;
    } // release
    if (m->u.adsr.state == 4) {
      float step = 1.f / (r * sr);
      env -= step;
      if (env <= 0.f) {
        env = 0.f;
        m->u.adsr.state = 0;
      }
    }
  }
  m->u.adsr.env = clampf(env, 0.f, 1.f);
  return m->u.adsr.env;
}

static inline float tick_vca(Module *m, float sig, float gain) {
  float g = m->u.vca.gain;
  if (gain != 0.f)
    g = gain; // external CV overrides internal gain if present
  return sig * g;
}

static inline float tick_mix4(Module *m, float a, float b, float c, float d) {
  return a * m->u.mix4.gains[0] + b * m->u.mix4.gains[1] +
         c * m->u.mix4.gains[2] + d * m->u.mix4.gains[3];
}

// ----------------------- PortAudio glue -----------------------------
typedef struct AudioCtx {
  Rack *rack;
  float *interleaved_tmp; // 2 channels temp (not strictly needed)
  int frames_left;        // stop after N frames (demo)
} AudioCtx;

static int audio_cb(const void *input, void *output, unsigned long frames,
                    const PaStreamCallbackTimeInfo *timeInfo,
                    PaStreamCallbackFlags statusFlags, void *userData) {
  (void)input;
  (void)timeInfo;
  (void)statusFlags;
  AudioCtx *ctx = (AudioCtx *)userData;
  Rack *r = ctx->rack;
  float *out = (float *)output;
  const float sr = (float)r->sample_rate;
  float outvals[MAX_MODULES][MAX_OUTPUTS];

  unsigned long todo = frames;
  if (ctx->frames_left >= 0 && ctx->frames_left < (int)frames)
    todo = (unsigned long)ctx->frames_left;

  for (unsigned long i = 0; i < todo; i++) {
    float L = 0.f, R = 0.f;
    // Per-sample compute in topological order
    for (int k = 0; k < r->topo_count; k++) {
      Module *m = &r->modules[r->topo_order[k]];
      switch (m->type) {
      case MOD_PARAM: {
        outvals[m->id][0] = tick_param(m);
      } break;
      case MOD_GATE: {
        float dt = 1.f / sr;
        outvals[m->id][0] = tick_gate(m, dt);
      } break;
      case MOD_VCO: {
        float cv = in_val(r, m, 0, outvals); // Hz CV add
        outvals[m->id][0] = tick_vco(m, sr, cv);
      } break;
      case MOD_LFO: {
        outvals[m->id][0] = tick_lfo(m, sr);
      } break;
      case MOD_ADSR: {
        float gate = in_val(r, m, 0, outvals);
        outvals[m->id][0] = tick_adsr(m, gate, sr);
      } break;
      case MOD_VCA: {
        float sig = in_val(r, m, 0, outvals);
        float gain = in_val(r, m, 1, outvals);
        outvals[m->id][0] = tick_vca(m, sig, gain);
      } break;
      case MOD_MIX4: {
        float a = in_val(r, m, 0, outvals);
        float b = in_val(r, m, 1, outvals);
        float c = in_val(r, m, 2, outvals);
        float d = in_val(r, m, 3, outvals);
        outvals[m->id][0] = tick_mix4(m, a, b, c, d);
      } break;
      case MOD_OUT: {
        float li = in_val(r, m, 0, outvals);
        float ri = in_val(r, m, 1, outvals);
        L = clampf(li, -1.f, 1.f);
        R = clampf(ri, -1.f, 1.f);
      } break;
      default:
        break;
      }
    }
    // write sample
    *out++ = L;
    *out++ = R;
  }

  if (ctx->frames_left >= 0) {
    ctx->frames_left -= (int)todo;
    if (ctx->frames_left <= 0)
      return paComplete;
  }
  return paContinue;
}

// ----------------------- Demo patch --------------------------------
static void build_demo_patch(Rack *r) {
  // Modules
  int pFreq = rack_add_module(r, MOD_PARAM, "ParamFreq", 0, 1);
  r->modules[pFreq].u.param.value = 220.f; // 220 Hz
  int gate = rack_add_module(r, MOD_GATE, "Gate", 0, 1);
  r->modules[gate].u.gate.length_s = 1.0f;
  int vco = rack_add_module(r, MOD_VCO, "VCO", 1, 1);
  r->modules[vco].u.vco.freq = 0.f; // use CV only
  int env = rack_add_module(r, MOD_ADSR, "ADSR", 1, 1);
  r->modules[env].u.adsr.a = 0.01f;
  r->modules[env].u.adsr.d = 0.25f;
  r->modules[env].u.adsr.s = 0.6f;
  r->modules[env].u.adsr.r = 0.5f;
  int vca = rack_add_module(r, MOD_VCA, "VCA", 2, 1);
  r->modules[vca].u.vca.gain = 0.0f; // controlled by env
  int out = rack_add_module(r, MOD_OUT, "OUT", 2, 0);

  // Wires (single-source per input)
  rack_connect(r, pFreq, 0, vco, 0); // ParamFreq -> VCO freq CV (Hz add)
  rack_connect(r, gate, 0, env, 0);  // Gate -> ADSR gate
  rack_connect(r, vco, 0, vca, 0);   // VCO -> VCA input
  rack_connect(r, env, 0, vca, 1);   // ADSR -> VCA gain
  rack_connect(r, vca, 0, out, 0);   // VCA -> OUT L
  rack_connect(r, vca, 0, out, 1);   // VCA -> OUT R

  rack_build_topo(r);
}

// ----------------------- Main --------------------------------------
int main(int argc, char **argv) {
  Rack rack;
  memset(&rack, 0, sizeof(rack));
  rack.sample_rate = 48000;
  rack.block_size = 64;
  rack.out_module = -1;

  int duration_s = 6; // default
  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "-d") == 0 && i + 1 < argc) {
      duration_s = atoi(argv[++i]);
    } else if (strcmp(argv[i], "-sr") == 0 && i + 1 < argc) {
      rack.sample_rate = atoi(argv[++i]);
    }
  }

  build_demo_patch(&rack);

  if (rack.out_module < 0) {
    fprintf(stderr, "No OUT module in rack.\n");
    return 1;
  }

  PaError err = Pa_Initialize();
  if (err != paNoError) {
    fprintf(stderr, "Pa_Initialize failed: %s\n", Pa_GetErrorText(err));
    return 1;
  }

  PaStream *stream = NULL;
  PaStreamParameters outParams;
  memset(&outParams, 0, sizeof(outParams));
  outParams.device = Pa_GetDefaultOutputDevice();
  if (outParams.device == paNoDevice) {
    fprintf(stderr, "No default output device.\n");
    Pa_Terminate();
    return 1;
  }
  const PaDeviceInfo *info = Pa_GetDeviceInfo(outParams.device);
  // Try stereo, fallback to mono if unavailable
  int chans = 2;
  if (info && info->maxOutputChannels < 2) {
    chans = info->maxOutputChannels > 0 ? info->maxOutputChannels : 1;
  }
  outParams.channelCount = chans;
  outParams.sampleFormat = paFloat32;
  outParams.suggestedLatency = info ? info->defaultLowOutputLatency : 0.02;
  outParams.hostApiSpecificStreamInfo = NULL;

  AudioCtx ctx;
  memset(&ctx, 0, sizeof(ctx));
  ctx.rack = &rack;
  ctx.interleaved_tmp = NULL;
  ctx.frames_left =
      duration_s >= 0 ? duration_s * rack.sample_rate : -1; // -1 = run forever

  err = Pa_OpenStream(&stream, NULL, &outParams, rack.sample_rate,
                      paFramesPerBufferUnspecified, paNoFlag, audio_cb, &ctx);
  if (err != paNoError) {
    fprintf(stderr, "Pa_OpenStream failed: %s\n", Pa_GetErrorText(err));
    Pa_Terminate();
    return 1;
  }

  err = Pa_StartStream(stream);
  if (err != paNoError) {
    fprintf(stderr, "Pa_StartStream failed: %s\n", Pa_GetErrorText(err));
    Pa_CloseStream(stream);
    Pa_Terminate();
    return 1;
  }

  // Busy wait until stream completes (for demo)
  while (Pa_IsStreamActive(stream) == 1) {
    Pa_Sleep(50);
  }

  Pa_StopStream(stream);
  Pa_CloseStream(stream);
  Pa_Terminate();

  return 0;
}

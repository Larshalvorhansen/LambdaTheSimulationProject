// Build: make   (see Makefile; expects raylib via pkg-config)
// Modes:
//   [1] Wire Mode: click an OUTPUT, drag, release on an INPUT
//   [2] Add Mode : click empty space to add a simple passthrough module
//   Right-click a cable to delete
//   Double-click a module -> logs a placeholder "editor" message

#include <math.h>
#include <raylib.h>
#include <raymath.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CANVAS_W 1100
#define CANVAS_H 680
#define PORT_R 7

typedef struct Module Module;

typedef enum { PORT_IN = 0, PORT_OUT = 1 } PortKind;

typedef struct {
  Module *module;
  char name[32];
  PortKind kind;
  float relx, rely;
  float value;
} Port;

typedef struct {
  Port *src; // out
  Port *dst; // in
} Cable;

struct Module {
  float x, y, w, h;
  char title[64];
  int numInputs, numOutputs;
  Port inputs[8];
  Port outputs[8];
};

typedef struct {
  Module modules[64];
  int moduleCount;

  Cable cables[256];
  int cableCount;

  Port *dragSrc;
  Vector2 tempMouse;

  int mode; // 0=wire, 1=add
} App;

// ---------------------------------------------------------------------------

static bool WithinCircle(Vector2 p, Vector2 c, float r) {
  Vector2 d = Vector2Subtract(p, c);
  return Vector2LengthSqr(d) <= r * r;
}

static Vector2 PortPos(const Port *p) {
  return (Vector2){p->module->x + p->relx, p->module->y + p->rely};
}

static void DrawWire(Port *src, Vector2 to, Color col, float thick) {
  Vector2 a = PortPos(src);
  Vector2 b = to;
  float mx = (a.x + b.x) * 0.5f;

  Vector2 p1 = a;
  Vector2 p2 = (Vector2){mx, a.y};
  Vector2 p3 = (Vector2){mx, b.y};
  Vector2 p4 = b;

  DrawLineEx(p1, p2, thick, col);
  DrawLineEx(p2, p3, thick, col);
  DrawLineEx(p3, p4, thick, col);
}

static void InitModule(Module *m, float x, float y, const char *title,
                       const char *const *inNames, int nIn,
                       const char *const *outNames, int nOut) {
  m->x = x;
  m->y = y;
  m->w = 210;
  m->h = 190;
  strncpy(m->title, title ? title : "Module", sizeof(m->title) - 1);
  m->numInputs = nIn;
  m->numOutputs = nOut;

  float top = 44.0f;
  float gapIn = (m->h - top - 16.0f) / (nIn > 0 ? nIn : 1);
  float gapOut = (m->h - top - 16.0f) / (nOut > 0 ? nOut : 1);

  for (int i = 0; i < nIn; i++) {
    Port *p = &m->inputs[i];
    p->module = m;
    p->kind = PORT_IN;
    p->relx = 18;
    p->rely = top + gapIn * i + 12;
    p->value = 0;
    strncpy(p->name, inNames[i], sizeof(p->name) - 1);
  }
  for (int i = 0; i < nOut; i++) {
    Port *p = &m->outputs[i];
    p->module = m;
    p->kind = PORT_OUT;
    p->relx = m->w - 18;
    p->rely = top + gapOut * i + 12;
    p->value = 0;
    strncpy(p->name, outNames[i], sizeof(p->name) - 1);
  }
}

static void AddModule(App *app, float x, float y, const char *title,
                      const char *const *inNames, int nIn,
                      const char *const *outNames, int nOut) {
  if (app->moduleCount >= (int)(sizeof(app->modules) / sizeof(app->modules[0])))
    return;
  InitModule(&app->modules[app->moduleCount++], x, y, title, inNames, nIn,
             outNames, nOut);
}

static void RemoveCableAt(App *app, int idx) {
  if (idx < 0 || idx >= app->cableCount)
    return;
  for (int i = idx; i < app->cableCount - 1; i++)
    app->cables[i] = app->cables[i + 1];
  app->cableCount--;
}

// ---------------------------------------------------------------------------

static void DrawModule(const Module *m) {
  // card
  DrawRectangleRounded((Rectangle){m->x, m->y, m->w, m->h}, 0.06f, 6,
                       (Color){31, 31, 36, 255});
  DrawRectangleRoundedLines((Rectangle){m->x, m->y, m->w, m->h}, 0.06f, 6,
                            (Color){122, 122, 136, 255});

  // title
  int tw = MeasureText(m->title, 16);
  DrawText(m->title, (int)(m->x + m->w / 2 - tw / 2), (int)(m->y + 8), 16,
           RAYWHITE);

  // ports + values
  for (int i = 0; i < m->numInputs; i++) {
    const Port *p = &m->inputs[i];
    Vector2 pos = PortPos(p);
    DrawCircleV(pos, PORT_R, (Color){255, 118, 118, 255});
    DrawText(p->name, (int)(pos.x + 13), (int)(pos.y - 7), 12,
             (Color){230, 230, 240, 255});
    char buf[64];
    snprintf(buf, sizeof(buf), "%.2f", p->value);
    DrawText(buf, (int)(pos.x - MeasureText(buf, 10) / 2), (int)(pos.y - 22),
             10, (Color){181, 227, 255, 255});
  }
  for (int i = 0; i < m->numOutputs; i++) {
    const Port *p = &m->outputs[i];
    Vector2 pos = PortPos(p);
    DrawCircleV(pos, PORT_R, (Color){68, 209, 122, 255});
    int nameW = MeasureText(p->name, 12);
    DrawText(p->name, (int)(pos.x - 13 - nameW), (int)(pos.y - 7), 12,
             (Color){230, 230, 240, 255});
    char buf[64];
    snprintf(buf, sizeof(buf), "%.2f", p->value);
    DrawText(buf, (int)(pos.x - MeasureText(buf, 10) / 2), (int)(pos.y - 22),
             10, (Color){181, 227, 255, 255});
  }
}

// input/output hit tests
static Port *HitInput(App *app, Vector2 pos) {
  for (int mi = 0; mi < app->moduleCount; mi++) {
    Module *m = &app->modules[mi];
    for (int i = 0; i < m->numInputs; i++) {
      Port *p = &m->inputs[i];
      if (WithinCircle(pos, PortPos(p), PORT_R + 2))
        return p;
    }
  }
  return NULL;
}

static Port *HitOutput(App *app, Vector2 pos) {
  for (int mi = 0; mi < app->moduleCount; mi++) {
    Module *m = &app->modules[mi];
    for (int i = 0; i < m->numOutputs; i++) {
      Port *p = &m->outputs[i];
      if (WithinCircle(pos, PortPos(p), PORT_R + 2))
        return p;
    }
  }
  return NULL;
}

// Return cable index if pointer near any segment; else -1
static int HitCableIndex(App *app, Vector2 pos) {
  for (int i = 0; i < app->cableCount; i++) {
    Cable *c = &app->cables[i];
    Vector2 a = PortPos(c->src);
    Vector2 b = PortPos(c->dst);
    float mx = (a.x + b.x) * 0.5f;
    Vector2 s1a = a, s1b = (Vector2){mx, a.y};
    Vector2 s2a = (Vector2){mx, a.y}, s2b = (Vector2){mx, b.y};
    Vector2 s3a = (Vector2){mx, b.y}, s3b = b;
    float th = 6.0f;
    if (CheckCollisionPointLine(pos, s1a, s1b, th) ||
        CheckCollisionPointLine(pos, s2a, s2b, th) ||
        CheckCollisionPointLine(pos, s3a, s3b, th))
      return i;
  }
  return -1;
}

// ---------------------------------------------------------------------------
// Evaluation

static void EvaluateModule(Module *m) {
  for (int i = 0; i < m->numOutputs; i++)
    m->outputs[i].value = 0.0f;

  if (strcmp(m->title, "Company X") == 0) {
    float subsidies = 0, revenues = 0, worker_output = 0;
    for (int i = 0; i < m->numInputs; i++) {
      if (strcmp(m->inputs[i].name, "subsidies") == 0)
        subsidies = m->inputs[i].value;
      else if (strcmp(m->inputs[i].name, "revenues") == 0)
        revenues = m->inputs[i].value;
      else if (strcmp(m->inputs[i].name, "worker_output") == 0)
        worker_output = m->inputs[i].value;
    }
    float salary = 0.6f * worker_output;
    float taxes = 0.2f * fmaxf(0.0f, revenues + subsidies - salary);
    for (int i = 0; i < m->numOutputs; i++) {
      if (strcmp(m->outputs[i].name, "salary") == 0)
        m->outputs[i].value = salary;
      else if (strcmp(m->outputs[i].name, "taxes") == 0)
        m->outputs[i].value = taxes;
    }
    return;
  }

  if (strcmp(m->title, "Worker Y") == 0) {
    float salary = 0, satisfaction = 0, goods = 0;
    for (int i = 0; i < m->numInputs; i++) {
      if (strcmp(m->inputs[i].name, "salary") == 0)
        salary = m->inputs[i].value;
      else if (strcmp(m->inputs[i].name, "satisfaction") == 0)
        satisfaction = m->inputs[i].value;
      else if (strcmp(m->inputs[i].name, "goods") == 0)
        goods = m->inputs[i].value;
    }
    float productive_work = (salary / 10000.0f * 0.5f + satisfaction * 0.3f +
                             goods / 10000.0f * 0.2f) *
                            10000.0f;
    float taxes = 0.2f * salary;
    for (int i = 0; i < m->numOutputs; i++) {
      if (strcmp(m->outputs[i].name, "productive_work") == 0)
        m->outputs[i].value = productive_work;
      else if (strcmp(m->outputs[i].name, "taxes") == 0)
        m->outputs[i].value = taxes;
    }
    return;
  }

  // default: first output = sum of inputs
  float sum = 0.0f;
  for (int i = 0; i < m->numInputs; i++)
    sum += m->inputs[i].value;
  if (m->numOutputs > 0)
    m->outputs[0].value = sum;
}

static void Simulate(App *app) {
  // zero inputs
  for (int i = 0; i < app->moduleCount; i++) {
    Module *m = &app->modules[i];
    for (int j = 0; j < m->numInputs; j++)
      m->inputs[j].value = 0.0f;
  }
  // propagate
  for (int i = 0; i < app->cableCount; i++) {
    Cable *c = &app->cables[i];
    c->dst->value += c->src->value;
  }
  // evaluate
  for (int i = 0; i < app->moduleCount; i++)
    EvaluateModule(&app->modules[i]);
}

// ---------------------------------------------------------------------------

int main(void) {
  SetConfigFlags(FLAG_WINDOW_RESIZABLE | FLAG_MSAA_4X_HINT);
  InitWindow(CANVAS_W, CANVAS_H, "Economic Patch Platform — C mini");
  SetTargetFPS(60);

  App app = {0};
  app.mode = 0; // wire

  // seed modules
  const char *cx_in[] = {"subsidies", "revenues", "worker_output"};
  const char *cx_out[] = {"taxes", "salary"};
  AddModule(&app, 200, 200, "Company X", cx_in, 3, cx_out, 2);

  const char *wy_in[] = {"salary", "satisfaction", "goods"};
  const char *wy_out[] = {"taxes", "productive_work"};
  AddModule(&app, 650, 200, "Worker Y", wy_in, 3, wy_out, 2);

  double lastTick = GetTime();
  double lastClickTime = 0.0;
  Vector2 lastClickPos = {0};

  while (!WindowShouldClose()) {
    Vector2 mouse = GetMousePosition();

    // mode hotkeys
    if (IsKeyPressed(KEY_ONE))
      app.mode = 0;
    if (IsKeyPressed(KEY_TWO))
      app.mode = 1;

    // clicks
    if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
      if (app.mode == 1) {
        // add if not on a port
        if (!HitInput(&app, mouse) && !HitOutput(&app, mouse)) {
          char name[32];
          snprintf(name, sizeof(name), "Module %d", app.moduleCount + 1);
          const char *in[] = {"in"};
          const char *out[] = {"out"};
          AddModule(&app, mouse.x - 105, mouse.y - 95, name, in, 1, out, 1);
        }
      } else {
        Port *out = HitOutput(&app, mouse);
        if (out) {
          app.dragSrc = out;
          app.tempMouse = mouse;
        }
      }
    }

    if (IsMouseButtonDown(MOUSE_BUTTON_LEFT) && app.dragSrc) {
      app.tempMouse = mouse;
    }

    if (IsMouseButtonReleased(MOUSE_BUTTON_LEFT) && app.dragSrc) {
      Port *in = HitInput(&app, mouse);
      if (in &&
          app.cableCount < (int)(sizeof(app.cables) / sizeof(app.cables[0]))) {
        app.cables[app.cableCount++] = (Cable){.src = app.dragSrc, .dst = in};
      }
      app.dragSrc = NULL;
    }

    if (IsMouseButtonPressed(MOUSE_BUTTON_RIGHT)) {
      int ci = HitCableIndex(&app, mouse);
      if (ci >= 0)
        RemoveCableAt(&app, ci);
    }

    // double-click detect => log "editor" notice
    if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
      double now = GetTime();
      if (now - lastClickTime < 0.25 &&
          Vector2Distance(lastClickPos, mouse) < 6.0f) {
        for (int i = 0; i < app.moduleCount; i++) {
          Module *m = &app.modules[i];
          if (CheckCollisionPointRec(mouse,
                                     (Rectangle){m->x, m->y, m->w, m->h})) {
            TraceLog(LOG_INFO, "Editor for '%s' not implemented in C demo.",
                     m->title);
            break;
          }
        }
      }
      lastClickTime = now;
      lastClickPos = mouse;
    }

    // tick ~8Hz
    double now = GetTime();
    if (now - lastTick >= 0.125) {
      Simulate(&app);
      lastTick = now;
    }

    // draw
    BeginDrawing();
    ClearBackground((Color){15, 15, 20, 255});

    DrawRectangle(0, 0, GetScreenWidth(), 36, (Color){23, 23, 27, 255});
    const char *modeStr = (app.mode == 0) ? "Wire Mode [1]" : "Add Mode [2]";
    DrawText(modeStr, 12, 10, 16, (Color){230, 230, 240, 255});
    DrawText(
        "Right-click cable to delete • Double-click module -> console note",
        220, 10, 16, (Color){184, 190, 201, 255});

    for (int i = 0; i < app.moduleCount; i++)
      DrawModule(&app.modules[i]);

    for (int i = 0; i < app.cableCount; i++) {
      Cable *c = &app.cables[i];
      DrawWire(c->src, PortPos(c->dst), (Color){57, 213, 255, 255}, 3.0f);
    }

    if (app.dragSrc) {
      DrawWire(app.dragSrc, app.tempMouse, (Color){245, 217, 10, 255}, 2.0f);
    }

    EndDrawing();
  }

  CloseWindow();
  return 0;
}

#include <iostream>
#include <cmath> // For sine wave calculation

// Constants
const double SAMPLE_RATE = 44100.0;
const double TWO_PI = 2.0 * M_PI;

// Base class for modules
class Module {
public:
  virtual double process(double input) = 0;
};

// LFO Module
class LFO : public Module {
private:
  double frequency;
  double phase = 0.0;

public:
  LFO(double freq = 1.0) : frequency(freq) {}

  double process(double input) override {
    double output = sin(phase);  // Simple sine wave for now

    // Update phase
    phase += TWO_PI * frequency / SAMPLE_RATE; 
    if (phase > TWO_PI) {
        phase -= TWO_PI; 
    }

    return output;
  }
};

// Oscilloscope Module
class Oscilloscope : public Module {
private:
   // Here you'd store samples for visualization 
   // (would likely depend on a GUI library for display)

public:
  double process(double input) override {
     // Store 'input' for visualization
     return input; // Pass-through for connection
  }
};

int main() {
  LFO myLFO(2.0); // LFO at 2 Hz
  Oscilloscope myScope;

  // Simulate audio processing loop
  for (int i = 0; i < SAMPLE_RATE; i++) {
    double lfoSignal = myLFO.process(0.0); // No 'real' input for this example
    double output = myScope.process(lfoSignal);

    // In a real application, 'output' would go to audio hardware
    std::cout << output << std::endl; 
  }

  return 0;
}

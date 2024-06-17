unsigned int Sampling_delay_us = 0;
const int num_times = 1000;
int index = 0;
int ADC_pin = A0;
int samples[num_times];
bool continue_program = true;

void setup() {
  Serial.begin(9600);

  pinMode(53, OUTPUT);
  digitalWrite(53, LOW);
  Serial.println("Setup complete. Ready to start.");
}

void loop() {
  digitalWrite(53, LOW);

  if (continue_program) {
    Serial.println("If conditional passed. Starting measurement.");
    digitalWrite(53, HIGH);
    for (index = 0; index < num_times; index++) {
      samples[index] = analogRead(ADC_pin);
      delayMicroseconds(Sampling_delay_us);
    }
    digitalWrite(53, LOW);
    Serial.println("Measurement complete.");
    continue_program = false;
  }

  // Add a small delay to prevent potential spurious behavior
  delay(10);
}

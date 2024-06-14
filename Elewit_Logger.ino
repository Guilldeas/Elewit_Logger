////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                                                                                            //
//                          ___  _____ ______   ________  _______   ________                                  //
//                         |\  \|\   _ \  _   \|\   ___ \|\  ___ \ |\   __  \                                 //
//                         \ \  \ \  \\\__\ \  \ \  \_|\ \ \   __/|\ \  \|\  \                                //
//                          \ \  \ \  \\|__| \  \ \  \ \\ \ \  \_|/_\ \   __  \                               //
//                           \ \  \ \  \    \ \  \ \  \_\\ \ \  \_|\ \ \  \ \  \                              //
//                            \ \__\ \__\    \ \__\ \_______\ \_______\ \__\ \__\                             //
//                             \|__|\|__|     \|__|\|_______|\|_______|\|__|\|__|                             //
//                                                                                                            //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////                                                                                           
//                                                                                                            //
//                                                                                                            //
// TO DO:                                                                                                     //
//   - Test higher frequency sampling with delayMicroseconds()                                                //
//   - Send data with only the relevant digits for the precision of the inbuilt ADC                           //
//                                                                                                            //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////



//---------------------------- Define Default Measurement Configuration --------------------------------------//
float Trigger_threshold_V = 1.0; // In volts
float ADC_voltage_ref = 5.0;
int number_samples = 10;
float Nyquist_frequency = 500; // In Hertz



//----------------------------------- Define code variables --------------------------------------------------//
int Trigger_threshold_counts = round(Trigger_threshold_V * 1023/ ADC_voltage_ref); // 1023 is the full scale count for the ADC reference
unsigned long Sampling_delay_ms = 1000 / ( 2 * Nyquist_frequency ); // In microseconds
int ADC_pin = A0;
bool Looking_for_trigger = true;
bool Program_finished = false;
int* ADC_values = nullptr;
int index = 0;
char Reconfigure = 'n';
#define pinMode(LED_BUILTIN, OUTPUT);
float ReadFloatFromSerial();
char ReadCharFromSerial();



//---------------------------------- Setup + Configuration ---------------------------------------------------//
void setup() {
  
  // Set up serial communication
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB
  }

  // Send Python the default values so that it can ask user if they want to reconfigure
  Serial.println(Trigger_threshold_V);
  Serial.println(ADC_voltage_ref);
  Serial.println(number_samples);
  Serial.println(Nyquist_frequency);

  // Listen to user for measurement configuration

  // Receiving a 'y' signals Arduino to request new variables for the measurement
  // Anything else makes it so the measurement is performed with default variables.
  Reconfigure = ReadCharFromSerial();
  if (Reconfigure == 'y') {
    Trigger_threshold_V = ReadFloatFromSerial();
    ADC_voltage_ref = ReadFloatFromSerial();
    number_samples = ReadFloatFromSerial();
    Nyquist_frequency = ReadFloatFromSerial();

    // Redo the calculation of measurement variables
    Trigger_threshold_counts = round(Trigger_threshold_V * 1023/ ADC_voltage_ref); // 1023 is the full scale count for the ADC reference
    Sampling_delay_ms = 1000 / ( 2 * Nyquist_frequency ); // In microseconds
  }

  // Create array dynamicaly
  ADC_values = new int[number_samples];
  
  //Initialize it by fulling it with zeroes
  for (index=0; index<number_samples; index++){

    ADC_values[index] = 0;

  }

  Serial.println("");
  Serial.println("  - Awaiting trigger...");

}

//----------------------------------------- Main loop --------------------------------------------------------//
void loop() {

  // Check for a trigger event
  while (Looking_for_trigger){

    if ( analogRead( ADC_pin ) >= Trigger_threshold_counts ){

      Looking_for_trigger = false;

      // Signal the user while reading is taking place
      digitalWrite(LED_BUILTIN, HIGH);

    }

  }

  // Record data for just one trigger
  if (not Program_finished){

    // Read ADC values
    Serial.println("  - Found Trigger event");
    Serial.println("  - Read stored ADC values");
    for (index=0; index<number_samples; index++){

      ADC_values[index] = analogRead( ADC_pin );
      delay(Sampling_delay_ms);

    }
    
    // Signal finished reading
    digitalWrite(LED_BUILTIN, LOW);
    
    // Send readings through serial communication
    Serial.println("  - Sending captured data in pairs of [V], [ms]");
    float timestamp = 0.0;
    float voltage = 0.0; 
    String CSV_pair;
    for (index=0; index<number_samples; index++){

      // Convert time and voltage values to more readable units
      timestamp = Sampling_delay_ms * (float)index; // Plot the *aproximate* time when the value was recorded
      voltage = ADC_voltage_ref * ( float(ADC_values[index]) / 1023.0 ); // Convert counts to volts
      
      // Construct and send a string with CSV format to output through COMs
      // CHECK: Decimal places have been set according to my assumptions of precision for the Arduino MEGA ADC and clock
      // that is millisecond accuravy and millivolt accuracy (5V_REF / 1024 ~ 5mV)
      CSV_pair = String(timestamp, 0) + "," + String(voltage, 3) + "\n";
      Serial.print(CSV_pair);

    }

    // When done sending tell python to stop listening and exit loop
    Program_finished = true;
    Serial.println("  - Close Communication");

  }  

}



//---------------------------------------------- Functions ----------------------------------------------------//

// This function reads a float from serial communication, this is trivial but the main purpouse of this
// aswell as it's sister ReadCharFromSerial() is to take care of a couple of problems when reading
// from serial, for instance, waiting for the port to connect at the very beginning of serial coms
// setup, waiting for user input to arrive to the serial input buffer, reading it and finaly
// emptying the buffer so that null characters and other stray chars might not remain in the buffer
// and throw off further readings.
float ReadFloatFromSerial(){
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB
  }
  
  // Wait for user input
  while (Serial.available() == 0) {
    ; // Do nothing until data is available
  }

  // Read user input
  float User_input = Serial.parseFloat();

  // Clear the serial input buffer by reading until no more characters are available
  // if not the null character at the end will be read as a 0 the next time this function
  // is called
  while (Serial.available() > 0) {
    Serial.read();
  }

  return User_input;
}


char ReadCharFromSerial(){
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB
  }

  // Wait for user input
  while (Serial.available() == 0) {
    ; // Do nothing until data is available
  }

  // Read user input
  char User_input = Serial.read();

  // Clear the serial input buffer by reading until no more characters are available
  // if not the null character at the end will be read as a 0 the next time this function
  // is called
  while (Serial.available() > 0) {
    Serial.read();
  }

  return User_input;
}

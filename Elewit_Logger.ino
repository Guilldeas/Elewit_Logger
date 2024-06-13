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


// Define user tweakable variables
float Trigger_threshold_V = 1.0; // In volts
float ADC_voltage_ref = 5.0;
const int number_samples = 100;
float Nyquist_frequency = 10; // In Hertz

// Define code variables
int Trigger_threshold_counts = round(Trigger_threshold_V * 1023/ ADC_voltage_ref); // 1023 is the full scale count for the ADC reference
unsigned long Sampling_delay_ms = 1000 / ( 2 * Nyquist_frequency ); // In microseconds
int ADC_pin = A0;
bool Looking_for_trigger = true;
bool Program_finished = false;
int ADC_values[number_samples];
int index = 0;

void setup() {

  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);

  // Set up serial communication
  Serial.begin(9600);

  //Initialize storing array to zeroes
  for (index=0; index<number_samples; index++){

    ADC_values[index] = 0;

  }

  Serial.println("");
  Serial.println("Awaiting trigger");

}


void loop() {

  // Check for a trigger event
  while (Looking_for_trigger){

    if (analogRead( ADC_pin ) >= Trigger_threshold_counts ){

      Looking_for_trigger = false;

      // Signal the user while reading is taking place
      digitalWrite(LED_BUILTIN, HIGH);

    }

  }

  // Record data for just one trigger
  if (not Program_finished){

    // Read ADC values
    Serial.println("Found Trigger event");
    Serial.println("Read stored ADC values");
    for (index=0; index<number_samples; index++){

      ADC_values[index] = analogRead( ADC_pin );
      delay(Sampling_delay_ms);

    }
    
    // Signal finished reading
    digitalWrite(LED_BUILTIN, LOW);
    
    // Send readings through serial communication
    Serial.println("Print samples in pairs of [V], [ms]");

    Serial.println("Sending captured data");
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
    Serial.println("Close Communication");

  }  

}


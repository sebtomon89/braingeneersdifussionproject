//This code was written to be easy to understand.
//Modify this code as you see fit.
//This code will output data to the Arduino serial monitor.
//Type commands into the Arduino serial monitor to control the pH circuit.
//This code was written in the Arduino 2.0 IDE
//This code was last tested 10/2022



String inputstring = "";                              //a string to hold incoming data from the PC
String sensorstring = "";                             //a string to hold the data from the Atlas Scientific product
boolean input_string_complete = false;                //have we received all the data from the PC
boolean sensor_string_complete = false;               //have we received all the data from the Atlas Scientific product
float pH;                                             //used to hold a floating point number that is the pH


void setup() {                                        //set up the hardware
  pinMode(12,OUTPUT);                                 // RELAY PIN  
  Serial.begin(9600);                                 //set baud rate for the hardware serial port_0 to 9600
  Serial3.begin(9600);                                //set baud rate for software serial port_3 to 9600
  inputstring.reserve(10);                            //set aside some bytes for receiving data from the PC
  sensorstring.reserve(30);                           //set aside some bytes for receiving data from Atlas Scientific product
}

void serialEvent() {                                  //if the hardware serial port_0 receives a char
  inputstring = Serial.readStringUntil(13);           //read the string until we see a <CR>
  input_string_complete = true;                       //set the flag used to tell if we have received a completed string from the PC
}


void serialEvent3() {                                 //if the hardware serial port_3 receives a char
  sensorstring = Serial3.readStringUntil(13);         //read the string until we see a <CR>
  sensor_string_complete = true;                      //set the flag used to tell if we have received a completed string from the PC
}


void loop() {                                         //here we go...


  if (input_string_complete == true) {                //if a string from the PC has been received in its entirety
    Serial3.print(inputstring);                       //send that string to the Atlas Scientific product
    Serial3.print('\r');                              //add a <CR> to the end of the string
    inputstring = "";                                 //clear the string
    input_string_complete = false;                    //reset the flag used to tell if we have received a completed string from the PC
  }


  if (sensor_string_complete == true) {               //if a string from the Atlas Scientific product has been received in its entirety
    //Serial.println(sensorstring);
    delay(2000);                                      //send that string to the PC's serial monitor
                                                      //uncomment this section to see how to convert the pH reading from a string to a float 
    if (isdigit(sensorstring[0])) {                   //if the first character in the string is a digit
      pH = sensorstring.toDouble();                   //convert the string to a floating point number so it can be evaluated by the Arduino
      if (pH > 7.3) {                              //if the pH is greater than or equal to 7.0
        digitalWrite(12,HIGH);                        //RELAY ON;
        delay(2000);   
        //Serial.println("high");                       //print "high" this is demonstrating that the Arduino is evaluating the pH as a number and not as a string
      }
      else {    
        digitalWrite(12,LOW);                         //RELAY ON;
        delay(2000);                                  //if the pH is less than or equal to 6.99
        //Serial.println("low");                        //print "low" this is demonstrating that the Arduino is evaluating the pH as a number and not as a string
      }

    Serial.println(pH);     
    }
   
  }
  sensorstring = "";                                  //clear the string:
  sensor_string_complete = false;                     //reset the flag used to tell if we have received a completed string from the Atlas Scientific product
}

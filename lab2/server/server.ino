void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);
}

void loop() {
  String data = "";
  String additionalData = " from Arduino";
  String terminator = ";";

  while(true) {
    if (Serial.available() > 0) {
      data += Serial.readString();
      if (data.indexOf(";") > 0) break;
    }
  }

  if (data.indexOf(";") > 0) {
    data.replace(";", "");
    data.replace("\n", "");
    data = data + additionalData + terminator;

    Serial.println(data);
  }
}

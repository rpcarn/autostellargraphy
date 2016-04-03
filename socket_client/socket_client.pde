import processing.net.*; 
import processing.video.*;

Client myClient; 
String dataIn; 
String na;
String[] na2;
String[][] na3;
//Capture cam;
//String[] cameras;

// easing variable
float easing = 1;

// calculate the new xpos value
float dx;
float dy;
float xpos = 0;
float ypos = 0;
float targetX = 0;
float targetY = 0;

void setup() { 
  size(640, 480);
   //cameras = Capture.list();
  //for(int i = 0;i<cameras.length;i++){
  //  println(cameras[i].toString());
  //}
  //  cam = new Capture(this, 320, 240, 30);
  //println(cameras[22]);
  //cam = new Capture(this, cameras[22]);
  //cam.start();
  
  // Connect to the local machine at port 5204.
  // This example will not run if you haven't
  // previously started a server on this port.
  myClient = new Client(this, "127.0.0.1", 5205); 
  frameRate(30);
} 

void draw() { 
  background(0);
  //if(cam.available()){
  //    cam.read();
  //}
  //image(cam,width,height);
  
  //ellipse(20,20,10,10);
  //if (myClient.available() > 0) { 
  dataIn = myClient.readString(); 
  //    na = dataIn; //print(dataIn);  
  myClient.clear();
  
  na = dataIn; 
  
  //println(na);
  //println(na==null);
  //println(na.length());
  
  if(na == null || na.length() == 0){
    ;
  }else{
    //println("in else");
    try{
      na2 = na.split(":");
      na3 = new String[na2.length][2];
      beginShape();
      for(int i=0;i<na2.length;i++){
        na3[i] = na2[i].split(","); 
      //}
            
      //for(int i=0;i<na3.length;i++){
        targetX = int(na3[i][0]);
        targetY = int(na3[i][1]);

        // calculate the new ypos value
        dx = targetX - xpos;
        if(abs(dx) > 1) {
          xpos += dx * easing;
        }        

        // calculate the new ypos value
        dy = targetY - ypos;
        if(abs(dy) > 1) {
          ypos += dy * easing;
        }

        ellipse(xpos, ypos,10,10);
        vertex(xpos, ypos);
        //vertex(targetX, targetY);
      }
      endShape(CLOSE); 
    }catch(ArrayIndexOutOfBoundsException e){
      println("Exception thrown : " + e); 
    }catch(Exception e){
      println("Exception thrown : " + e); 
  }
}

//    myClient.write("OK!");
//} 
} 
// Called after form input is processed
firebase.initializeApp({
    apiKey: "AIzaSyBEF9ZwS0eZLMWhu0URb-kcYT4Zboyl8AE",
    authDomain: "embeddedsymv1.firebaseapp.com",
    databaseURL: "https://embeddedsymv1-default-rtdb.firebaseio.com",
    projectId: "embeddedsymv1",
    storageBucket: "embeddedsymv1.appspot.com",
    messagingSenderId: "101226855407",
    appId: "1:101226855407:web:b9ef97cf39b76d2b13941a",
    measurementId: "G-XX47NKF6VP"
    });
    const db = firebase.firestore();

var messagetext;
var altitude_count = 1000;
var temp_count = 24;
var where = "start";
function startConnect() {
    
    // Generate a random client ID
    clientID = "clientID-" + parseInt(Math.random() * 100);
    const d = new Date();
    // Fetch the hostname/IP address and port number from the form
    where = document.getElementById("host").value;
    getFireData(where);
    //document.getElementById("messages").innerHTML += '<span> Starting a session. </span><br/>';
    //port = document.getElementById("port").value;
    host = "broker.mqttdashboard.com"
    port = 8000
    // Print output for the user in the messages div
    //document.getElementById("messages").innerHTML += '<span>' + d.getTime() + 'Connecting to: ' + host + ' on port: ' + port + '</span><br/>';
    //document.getElementById("messages").innerHTML += '<span>'  +  d.getTime() + 'Using the following client value: ' + clientID + '</span><br/>';

    // Initialize new Paho client connection
    client = new Paho.MQTT.Client(host, Number(port), clientID);

    // Set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    var checkBox1 = document.getElementById("scales1");
    var checkBox2 = document.getElementById("scales2");
    var checkBox3 = document.getElementById("scales3");
    var checkBox4 = document.getElementById("scales4");
    var checkBox5 = document.getElementById("scales5");
    var checkBox6 = document.getElementById("scales6");
    var checkBox7 = document.getElementById("scales7");
      if ((checkBox1.checked == true)||(checkBox2.checked == true)||(checkBox3.checked == true)||(checkBox4.checked == true)||(checkBox5.checked == true)||(checkBox6.checked == true)||(checkBox7.checked == true)){
        console.log("checked");
        messagetext = "1"
      } else {
        console.log("not checked");
        messagetext = "0"
      }
    // Connect the client, if successful, call onConnect function
    client.connect({ 
        onSuccess: onConnect,
    });
}


// Called when the client connects
function onConnect() {
    // Fetch the MQTT topic from the form
    //topic = document.getElementById("topic").value;
    topic = "IC.embedded/symbiotic/#"
    // Print output for the user in the messages div
    //document.getElementById("messages").innerHTML += '<span>Subscribing to: ' + topic + '</span><br/>';

    // Subscribe to the requested topic
    client.subscribe(topic);
    //message = new Paho.MQTT.Message("Hello World 2");
    message = new Paho.MQTT.Message(messagetext);
    message.destinationName = "IC.embedded/symbioticback/";
    client.send(message);
    
}

// Called when the client loses its connection
function onConnectionLost(responseObject) {
    document.getElementById("messages").innerHTML += '<span>ERROR: Connection lost</span><br/>';
    if (responseObject.errorCode !== 0) {
        document.getElementById("messages").innerHTML += '<span>ERROR: ' + + responseObject.errorMessage + '</span><br/>';
    }
}

// Called when a message arrives
function onMessageArrived(message) {
    console.log("onMessageArrived: " + message.payloadString);
    //document.getElementById("messages").innerHTML += '<span>Topic: ' + message.destinationName + '  | ' + message.payloadString + '</span><br/>';
    if(message.destinationName === "IC.embedded/symbiotic/data") {
        //document.getElementById("messages").innerHTML += '<span> This is a data message. </span><br/>';
        myObj = JSON.parse(message.payloadString)
        addFireData(myObj.time,myObj.altitude,myObj.temperature,myObj.pressure,myObj.bearings)
        document.getElementById("messages").innerHTML += '<span>Time: ' + myObj.time + '</span>';
        document.getElementById("messages").innerHTML += '<span>, Altitude: ' + myObj.altitude + '</span>';
        document.getElementById("messages").innerHTML += '<span> meters, Temperature: ' + myObj.temperature + '</span>';
        document.getElementById("messages").innerHTML += '<span> degC, Pressure: ' + myObj.pressure + '</span>';
        document.getElementById("messages").innerHTML += '<span> hPa, Bearings: ' + myObj.bearings + ' deg</span><br/>';
    }
    if(message.destinationName === "IC.embedded/symbiotic/warning/pres") {
        //document.getElementById("messages").innerHTML += '<span> This is a warning message. </span><br/>';
        document.getElementById("warnings").innerHTML +='<span>' + message.payloadString + '</span><br/>';
        alert(message.payloadString);
        updateScroll();
    }
    if(message.destinationName === "IC.embedded/symbiotic/warning/temp") {
        //document.getElementById("messages").innerHTML += '<span> This is a warning message. </span><br/>';
        document.getElementById("warnings").innerHTML += '<span>' + message.payloadString + '</span><br/>';
        alert(message.payloadString);
        updateScroll();
    }
    if(message.destinationName === "IC.embedded/symbiotic/warning/alt") {
        //document.getElementById("messages").innerHTML += '<span> This is a warning message. </span><br/>';
        document.getElementById("warnings").innerHTML += '<span>' + message.payloadString + '</span><br/>';
        alert(message.payloadString);
        updateScroll();
    }
    if(message.destinationName === "IC.embedded/symbiotic/warning/no") {
        //document.getElementById("messages").innerHTML += '<span> This is a warning message. </span><br/>';
        document.getElementById("warnings").innerHTML += '<span>' + message.payloadString + '</span><br/>';
        updateScroll();
    }
    if(message.destinationName === "IC.embedded/symbiotic/changes") {
        //document.getElementById("messages").innerHTML += '<span> This is a warning message. </span><br/>';
        document.getElementById("changes").innerHTML += '<span>' + message.payloadString + '</span><br/>';
        updateScroll();
    }
    //addFireData(altitude_count,temp_count);
    //altitude_count++;
    //temp_count++;
    updateScroll();
}

// Called when the disconnection button is pressed
function startDisconnect() {
    client.disconnect();
    document.getElementById("messages").innerHTML += '<span>Disconnected</span><br/>';
}

function AutoRefresh( t ) {
    setTimeout("location.reload(true);", t);
}

function addFireData(tim,alt,temp,pres,bear){
    const d = new Date();
    var timenowis = d.getTime() + "0";
    console.log(timenowis);
    db.collection(where).doc(timenowis).set({
        time: tim,
        altitude: alt,
        temperature: temp,
        pressure: pres,
        bearings: bear
    })
    .then((docRef) => {
        console.log("Document written with ID: ", docRef.id);
    })
    .catch((error) => {
        console.error("Error adding document: ", error);
    });
}

function getFireData(whereDoc){
    db.collection(whereDoc).get().then((querySnapshot) => {
        querySnapshot.forEach((doc) => {
            console.log(doc.data());
            document.getElementById("messages").innerHTML += '<span>Time: ' + doc.data().time + '</span>';
            document.getElementById("messages").innerHTML += '<span>, Altitude: ' + doc.data().altitude + '</span>';
            document.getElementById("messages").innerHTML += '<span> meters, Temperature: ' + doc.data().temperature + '</span>';
            document.getElementById("messages").innerHTML += '<span> degC, Pressure: ' + doc.data().pressure + '</span>';
            document.getElementById("messages").innerHTML += '<span> hPa, Bearings: ' + doc.data().bearings + ' deg</span><br/>';
            updateScroll();
        });
    });
}

function updateScroll() {
    var element = document.getElementById("messages");
    element.scrollTop = element.scrollHeight;
    var element1 = document.getElementById("warnings");
    element1.scrollTop = element1.scrollHeight;
    var element2 = document.getElementById("changes");
    element2.scrollTop = element2.scrollHeight;
}
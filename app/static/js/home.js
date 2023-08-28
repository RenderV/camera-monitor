const audio = new Audio("/static/sounds/notification.mp3");
var firstStream = true;

if (typeof(EventSource) !== 'undefined') {
    var source = new EventSource("/report/stream");
    source.onmessage = function(event) {
        if (firstStream){
            firstStream = false;
        } else {
            audio.pause();
            audio.currentTime = 0;
            audio.play();
        }
        var report = JSON.parse(event.data);
        console.log(report.date)
        let report_date = new Date(report.date+"Z")

        document.getElementById("report-local").innerText = "Local: "+report.location;
        document.getElementById("report-hora").innerText = "Hora: "+report_date.toLocaleTimeString();
        document.getElementById("report-data").innerText = "DETECÇÃO EM "+report_date.toLocaleDateString();
        document.getElementById("report-img").setAttribute('src', '/static/imgs/uploads/'+report.image_url);

    };
} else {
    console.log("Server-Sent Events not supported by your browser.");
}
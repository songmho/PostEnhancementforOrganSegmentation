function CircularProgress(progressId, iaProgressCanvasId, aProgressCanvasId) {
    this.caption = $('#' + progressId + '.progress-bar p');
    this.iProgress = document.getElementById(iaProgressCanvasId);
    this.aProgress = document.getElementById(aProgressCanvasId);
    this.iProgressCTX = this.iProgress.getContext('2d');
}

CircularProgress.prototype.init = function() {
    this.iProgressCTX.lineCap = 'square';

    //outer ring
    this.iProgressCTX.beginPath();
    this.iProgressCTX.lineWidth = 15;
    this.iProgressCTX.strokeStyle = '#e1e1e1';
    this.iProgressCTX.arc(137.5,137.5,129,0,2*Math.PI);
    this.iProgressCTX.stroke();

    //progress bar
    this.iProgressCTX.beginPath();
    this.iProgressCTX.lineWidth = 0;
    this.iProgressCTX.fillStyle = '#e6e6e6';
    this.iProgressCTX.arc(137.5,137.5,121,0,2*Math.PI);
    this.iProgressCTX.fill();

    //progressbar caption
    this.iProgressCTX.beginPath();
    this.iProgressCTX.lineWidth = 0;
    this.iProgressCTX.fillStyle = '#fff';
    this.iProgressCTX.arc(137.5,137.5,100,0,2*Math.PI);
    this.iProgressCTX.fill();

};

CircularProgress.prototype.drawProgress = function(percentage) {
    var barCTX = this.aProgress.getContext("2d");
    var quarterTurn = Math.PI / 2;
    var endingAngle = ((2*percentage) * Math.PI) - quarterTurn;
    var startingAngle = 0 - quarterTurn;

    this.aProgress.width = this.aProgress.width;
    barCTX.lineCap = 'square';

    barCTX.beginPath();
    barCTX.lineWidth = 20;
    barCTX.strokeStyle = '#D76474';
    barCTX.arc(137.5,137.5,111,startingAngle, endingAngle);
    barCTX.stroke();

    if(percentage < 0) percentage = 0;
    else if (percentage > 100) percentage = 100;
    this.caption.text( (parseInt(percentage, 10)) + '%');
};
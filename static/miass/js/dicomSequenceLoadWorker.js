/**
 * Created by hanter on 2016. 4. 14..
 */
//onmessage = function(event) {
//    var receiveData = event.data;
//    var cornerstone = receiveData.cornerstone;
//    var files = receiveData.files;
//
//    var dicomSeq = [];
//    for (var idx = 0; idx < files.length; idx++) {
//        try {
//            var wadoURI = "wadouri:" + makeURL(files[idx]);
//            cornerstone.loadAndCacheImage(wadoURI).then(function (image) {
//                dicomSeq.push(image)
//            });
//        } catch (err) {
//            showImageViewerLoader(false);
//            openModal(err, "DICOM Loading Failed");
//            return;
//        }
//    }
//
//    var loadWaitingTimeInterval = setInterval(function() {
//        if(dicomSeq.length == files.length) {
//            clearInterval(loadWaitingTimeInterval);
//            postMessage(dicomSeq);
//        }
//    }, 50);
//};

importScripts('/static/miass/js/constants.js',
              '/static/lib/jquery/workerFakeDOM.js',
              '/static/lib/jquery/jquery-2.2.0.min.js',
              '/static/lib/wado/conerstone/cornerstone.js');

var loadwaitingInterval = null;

onmessage = function(event) {
    //console.log(event);
    var receiveData = event.data;
    var files = receiveData.files;
    var imageInfo = receiveData.imageInfo;

    loadwaitingInterval = null;
    var fileCnt = files.length, loadCnt = 0;
    dicomSeq = [];
    for (var idx = 0; idx < files.length; idx++) {
        var wadoURI = "wadouri:" + makeURL(imageInfo, files[idx]);
        cornerstone.loadAndCacheImage(wadoURI).then(function (image) {
            //console.log(image);
            dicomSeq.push(image);
            loadCnt++;
        }, function(err) {
            console.log(err);
            fileCnt--;
        });
    }

    postMessage(receiveData);
    close();
};

function makeURL(imageInfo, relativeURL) {
    return SERVER_ADDRESS + '/api/archive?image_user_id=' + imageInfo['user_id']
        + '&image_id=' + imageInfo['image_id']
        + '&image_dir=' + relativeURL;
}

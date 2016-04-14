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

onmessage = function(event) {
    console.log(event);

    var receiveData = event.data;
    console.log(receiveData);

    postMessage(receiveData);
}
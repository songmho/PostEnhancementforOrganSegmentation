(function () {
    cornerstoneWADOImageLoader.external.cornerston = cornerston;

    var config = {
        maxWebWorkers: navigator.hardwareConcurrency || 1,
        startWebWorkersOnDemand : true,
    };
    cornerstoneWADOImageLoader.webWorkerManager.initialize(config);

    cornerston.registerImageLoader("viewer", loadImage);

})(jQuery);

function loadImage(imageId) {
        // create a deferred object
        var deferred = $.Deferred();

        // Make the request for the DICOM data
        var oReq = new XMLHttpRequest();
        oReq.open("get", imageId, true);
        oReq.responseType = "arraybuffer";
        oReq.onreadystatechange = function(oEvent) {
            if (oReq.readyState === 4)
            {
                if (oReq.status == 200) {
                    // request succeeded, create an image object and resolve the deferred
                    // Code to parse the response and return an image object omitted.....
                    var image = createImageObject(oReq.response);
                    // return the image object by resolving the deferred
                    deferred.resolve(image);
                }
                else {
                    // an error occurred, return an object describing the error by rejecting
                    // the deferred
                    deferred.reject({error: oReq.statusText});
                }
            }
        };
        oReq.send();

        // return the pending deferred object to cornerstone so it can setup callbacks to be
        // invoked asynchronously for the success/resolve and failure/reject scenarios.
        return deferred;
    }
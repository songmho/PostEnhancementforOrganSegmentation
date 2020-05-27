// // This script will load the WebWorkers and Codecs from unpkg url
//
// try {
//   window.cornerstoneWADOImageLoader.webWorkerManager.initialize({
//     maxWebWorkers: 4,
//     startWebWorkersOnDemand: true,
//     webWorkerTaskPaths: [],
//     taskConfiguration: {
//       decodeTask: {
//         initializeCodecsOnStartup: false,
//         usePDFJS: false,
//         strict: true
//       }
//     }
//   });
// } catch (error) {
//   throw new Error('cornerstoneWADOImageLoader is not loaded');
// }
//


try {
  cornerstoneWADOImageLoader.external.cornerstone = cornerstone;
  cornerstoneWADOImageLoader.external.dicomParser = dicomParser;
  cornerstoneTools.external.cornerstone = cornerstone;
  cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
  cornerstoneWADOImageLoader.webWorkerManager.initialize({
    maxWebWorkers: navigator.hardwareConcurrency || 1,
    startWebWorkersOnDemand: true,
    webWorkerPath: "cornerstoneWADOImageLoaderWebWorker.min.js",
    taskConfiguration: {
      'decodeTask': {
        loadCodecsOnStartup : true,
        initializeCodecsOnStartup: false,
        codecsPath: "cornerstoneWADOImageLoaderCodecs.min.js"
      }
    }
  });
} catch (e) {
  // Already initialized
  console.log(e)
}
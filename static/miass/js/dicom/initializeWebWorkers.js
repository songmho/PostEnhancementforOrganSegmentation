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
  cornerstoneTools.init({
    /**
     * When cornerstone elements are enabled,
     * should `mouse` input events be listened for?
     */
    mouseEnabled: true,
    /**
     * When cornerstone elements are enabled,
     * should `touch` input events be listened for?
     */
    touchEnabled: true,
    /**
     * A special flag that synchronizes newly enabled cornerstone elements. When
     * enabled, their active tools are set to reflect tools that have been
     * activated with `setToolActive`.
     */
    globalToolSyncEnabled: false,
    /**
     * Most tools have an associated canvas or SVG cursor. Enabling this flag
     * causes the cursor to be shown when the tool is active, bound to left
     * click, and the user is hovering the enabledElement.
     */
    showSVGCursors: false,
  });
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

  cornerstoneTools.init();
} catch (e) {
  // Already initialized
  console.log(e)
}
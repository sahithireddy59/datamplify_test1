// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
export const environment = {
  // production: true,
  firebase: {
    apiKey: "***************************************",
    authDomain: "************************",
    projectId: "***********************************",
    storageBucket: "************************",
    messagingSenderId: "*********************",
    appId: "*******************************************",
    measurementId: "*********************"
  },
  production: false,
  // dev 
  // apiUrl:'http://13.57.231.251:50/v1',
    //  //local
    //  apiUrl:'http://172.16.16.81:8000/v1',
    // QA server
    // apiUrl:'http://13.52.99.241:80/v1',
        // apiUrl:'https://api.qa.insightapps.ai/v1',
        airflowApiUrl: 'http://127.0.0.1:8001',
        // airflowApiUrl: 'http://3.101.147.3:8080',
    // demo url
      // apiUrl:'https://api.insightapps.ai/v1'

    //datamplify dev
    // apiUrl: 'http://172.16.17.159:80/v1',
    // apiUrl: 'http://172.16.16.135:8000/v1',
   // apiUrl: 'http://202.65.155.123:80/v1'
      apiUrl: 'http://127.0.0.1:8000/v1'

};


/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.

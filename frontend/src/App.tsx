import { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { Upload } from './Upload'
import { ImagePreview } from './ImagePreview';
import { Status } from './Status';
import { ChakraProvider } from '@chakra-ui/react';
const rootURL = import.meta.env.VITE_DOMAIN;

function App() {
  const [batchToken, setbatchToken] = useState<string>();
  const [processStatus, setProcessStatus] = useState<string>('');
  const [processStatusDetail, setProcessStatusDetail] = useState<string>('');
  const [downloadStatus, setDownloadStatus] = useState<boolean>(false);
  const [processedImage, setProcessedImage] = useState<any>();
  const [pollIntervalTick, setPollIntervalTick] = useState<Date>();
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [imageData, setImageData] = useState<any>();
  const [activeView, setActiveView] = useState<JSX.Element>(
    <Upload setSubmitted={setSubmitted} setImageData={setImageData}/>
    //<ImagePreview originalImageData={} processedImageData={}>
  )


  // Declare a time interval we want to run. Adapted from Zahra Shahrouzi @ https://stackoverflow.com/questions/39426083/update-react-component-every-second/59861536
  useEffect(() => {
    const pollInterval = setInterval(() => setPollIntervalTick(new Date()), 3000);
    return () => {
      clearInterval(pollInterval);
    };
  }, []);

  // Submit image and wait for batch ticket
  useEffect(() => {
    if (submitted && typeof imageData !== 'undefined') {
      const data = new FormData();
      data.append("image", imageData);
      console.log("submitting image");
      (
        async function sendImage() {
          await axios.post(`${rootURL}/upload`, data)
          .then(function (res) {
            // Capture batch token
            setbatchToken(res.data.batch_token);
          })
          .catch(function(err) {
            // TODO: Pop error toast
            console.log(err);
          })
          .finally(function() {})
        }
      )();
    }
  }, [imageData, submitted])

  // Request status to receive a reply when processing is complete
  useEffect(() => {
    if (batchToken !== undefined && batchToken.length > 1 && !downloadStatus) {
      (
        async function getStatus() {
          await axios.get(`${rootURL}/batch?token=${batchToken}`)
          .then(function (res) {
            setProcessStatus(res.data.status);
            setProcessStatusDetail(res.data.detail);

            // Stop checking if processing was successful
            if (res.data.status === 'completed') {
              setDownloadStatus(true);
            }
          })
          .catch(function(err) {
            console.log(err);
          })
          .finally(function() {
            console.log(`batch status checked at ${pollIntervalTick}`);
          })
        }
      )();
    }
  }, [batchToken, pollIntervalTick, downloadStatus])

  // After success message, request download
  useEffect(() => {
    if (downloadStatus) {
      (
        async function downloadImage() {
          await axios.get(`${rootURL}/download?token=${batchToken}&original=true`, {
            responseType: 'blob'
          })
          .then((res) => {
            // TODO: Display downloading spinner
            setProcessedImage(URL.createObjectURL(res.data));
          })
          .catch(function(err: any) {
            // TODO: Pop toast with error
            console.log(err);
          })
          .finally(function() {
            setActiveView(<ImagePreview originalImageData={imageData} processedImageData={imageData}/> )
          })
        }
      )();
    }
  }, [downloadStatus])

  return (
    <ChakraProvider>
      <div className="d-flex flex-column min-vh-100 container justify-content-center" id="body">
        <div className="section align-middle">
          <div id="header" className="row justify-content-center">
            <div className="m-3 col-10">
              <h1 className="text-center">Deep Learning Watermark Removal</h1>
              </div>
           </div>
            {activeView}
            {/* <Status /> */}
        </div>
      </div>
    </ChakraProvider>
  )
}

export default App

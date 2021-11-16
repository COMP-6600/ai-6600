import { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { ChakraProvider, useToast } from '@chakra-ui/react';
import { Upload } from './Upload'
import { ImagePreview } from './ImagePreview';
import { Status } from './Status';
const rootURL = import.meta.env.VITE_DOMAIN;

function App() {
  // Interval timer for request sending
  const [pollIntervalTick, setPollIntervalTick] = useState<Date>();

  // Flags
  const [batchToken, setBatchToken] = useState<string>();
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [downloadStatus, setDownloadStatus] = useState<boolean>(false);
  const [processStatus, setProcessStatus] = useState<string>('');
  const [processStatusDetail, setProcessStatusDetail] = useState<string>('');
  const [processStatusOpen, setProcessStatusOpen] = useState<boolean>(false)
  const [secondsElapsed, setSecondsElapsed] = useState<number>(-1);
  const [globalHalt, setGlobalHalt] = useState<boolean>(false)

  // Images
  const [originalImageData, setOriginalImageData] = useState<any>();
  const [processedImageData, setProcessedImage] = useState<any>();

  // View
  const [activeView, setActiveView] = useState<JSX.Element>(
    <Upload setSubmitted={setSubmitted} setImageData={setOriginalImageData}/>
  )

  // Global Toast
  const toast = useToast();

  // Declare a time interval we want to run. Adapted from Zahra Shahrouzi @ https://stackoverflow.com/questions/39426083/update-react-component-every-second/59861536
  useEffect(() => {
    const pollInterval = setInterval(() =>
      setPollIntervalTick(
        new Date()), 1000
    );
    return () => {
      clearInterval(pollInterval);
    };
  }, []);

  // Submit image and wait for batch ticket
  useEffect(() => {
    if (submitted && typeof originalImageData !== 'undefined' && !globalHalt) {
      const data = new FormData();
      data.append("image", originalImageData);
      (
        async function sendImage() {
          await axios.post(`${rootURL}/upload`, data)
          .then(function (res) {
            // Capture batch token
            setBatchToken(res.data.batch_token);
          })
          .catch(function(err) {
            // Pop toast with error
            console.log(err);
            (() =>
              toast({
                title: "Error",
                description: "There was an error submitting the image for processing.",
                status: "error",
                duration: 5000,
                isClosable: true,
              })
            )();
            setGlobalHalt(true);
          })
          .finally(function() {})
        }
      )();
    }
  }, [originalImageData, submitted, globalHalt])

  // Request status to receive a reply when processing is complete
  useEffect(() => {
    if (batchToken !== undefined && batchToken.length > 1 && !downloadStatus && !globalHalt) {
      (
        async function getStatus() {
          // Pop open status windows and initialize values
          if (secondsElapsed === -1) {
            setProcessStatus("Queued");
            setProcessStatusDetail("The image is in line for processing.");
          }
          setSecondsElapsed(secondsElapsed + 1);
          setProcessStatusOpen(true)

          // Request status continually and update values
          await axios.get(`${rootURL}/batch?token=${batchToken}`)
          .then(function (res) {
            setProcessStatus(res.data.status);
            setProcessStatusDetail(res.data.detail);

            // Stop checking if processing was successful
            if (res.data.status === 'completed') {
              setDownloadStatus(true);
              setProcessStatus("Downloading");
              setProcessStatusDetail("The processed image is now being downloaded.");
            }
          })
          .catch(function(err) {
            // Pop toast with error
            setProcessStatusOpen(false);
            console.log(err);
            (() =>
              toast({
                title: "Error",
                description: "There was an error requesting the processing status.",
                status: "error",
                duration: 5000,
                isClosable: true,
              })
            )();
            setGlobalHalt(true);
          })
        }
      )();
    }
  }, [batchToken, pollIntervalTick, downloadStatus, globalHalt])

  // After success message, request download
  useEffect(() => {
    if (downloadStatus && !globalHalt) {
      (
        async function downloadProcessedImage() {
          await axios.get(`${rootURL}/download?token=${batchToken}`, {
            responseType: 'blob'
          })
          .then((res) => {
            // Display downloading spinner
            setProcessStatusOpen(false);
            setProcessedImage(URL.createObjectURL(res.data));
          })
          .catch(function(err: any) {
            // Pop toast with error
            setProcessStatusOpen(false);
            console.log(err);
            (() =>
              toast({
                title: "Error",
                description: "There was an error downloading the processed image.",
                status: "error",
                duration: 5000,
                isClosable: true,
              })
            )();
            setGlobalHalt(true);
          })
          .finally(function() {
            // Use global halt flag to avoid displaying on error
            // if (!globalHalt) {
            //   setActiveView(<ImagePreview originalImageData={originalImageData} processedImageData={processedImageData}/> )
            // }
          })
        }
      )();
    }
  }, [downloadStatus, globalHalt])

  // Run only when processed image data has been provided
  useEffect(() => {
    if (typeof processedImageData !== 'undefined') {
      setActiveView(<ImagePreview originalImageData={originalImageData} processedImageData={processedImageData}/>)
    }
  }, [processedImageData])

  // Return component
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
            <Status status={processStatus} detail={processStatusDetail} secondsElapsed={secondsElapsed} popOpen={processStatusOpen}/>
        </div>
      </div>
    </ChakraProvider>
  )
}

export default App

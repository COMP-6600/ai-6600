## Upload Directory
+ All files uploaded through the site will land here.
+ They will be indexed with a UUID that is stored in a database and assigned to a job,
and a header will be sent back to the user containing the value.
+ The job and image name are both the UUID and are passed back to the client as a batch_token or a header.
+ For the user to be able to receive the response image, the site can implement JS to periodically poll a job endpoint along with
the UUID given as a header, or use Websockets to keep the connection open until processing is completed by the batch runner.
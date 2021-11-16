import { useState, useEffect } from 'react'
import {
  Button
} from '@chakra-ui/react';

export function Upload({ setSubmitted, setImageData }: { setSubmitted: any, setImageData: any }): JSX.Element {
  const [loading, setLoading] = useState<boolean>(false);


  return (
    <form action="#" encType="multipart/form-data" method="post" id="formCont">
      <div className="m-3 row justify-content-center">
        <div className="col-5">
          <input
            id="file-selector"
            className="form-control"
            accept="image/png, image/jpeg"
            name="image"
            type="file"
            onChange={({ target }) => setImageData((target.files as FileList)[0])}
          />
          <small className="form-text text-muted">Maximum image size is 5MB.</small>
        </div>
      </div>
      <div className="m-4 row justify-content-center">
        {/* <!-- Firefox does not seem to respect minimum width requirements with btn-block, so we can set the value as an override--> */}
        <div className="col-2">
          <Button
            size="lg"
            colorScheme="gray"
            type="reset"
            isFullWidth={true}
          >
            Clear
          </Button>                        
        </div>
        <div className="col-2">
          <Button
            size="lg"
            colorScheme="green"
            onClick={() => setSubmitted(true)}
            type="button"
            isFullWidth={true}
            isLoading={loading}
            loadingText="Uploading"
          >
            Upload
          </Button>
        </div>
      </div>
    </form>
  )
}
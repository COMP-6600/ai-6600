import {
  Image, Flex, Spacer, Heading, SimpleGrid
} from '@chakra-ui/react';


export function ImagePreview({originalImageData, processedImageData} : {originalImageData: any, processedImageData: any}): JSX.Element {
  return (
    <>
      <Flex color="white" rounded={15} alignContent="center" alignItems="center" height="inherit" width="inherit" direction="row" paddingTop="20">
        <SimpleGrid justifyItems="center">
          <Heading padding="4" fontFamily="Montserrat, sans-serif" fontSize="2.3em">Original Image</Heading>
          <Image width="calc(100vw / 3.2)" fit="fill" src={URL.createObjectURL(originalImageData)}/>
        </SimpleGrid>
        <Spacer/>
        <SimpleGrid justifyItems="center">
          <Heading padding="4" fontFamily="Montserrat, sans-serif" fontSize="2.3em">Processed Image</Heading>
          <Image width="calc(100vw / 3.2)" fit="fill" src={URL.createObjectURL(processedImageData)}/>
        </SimpleGrid>
      </Flex>
    </>
  )
}
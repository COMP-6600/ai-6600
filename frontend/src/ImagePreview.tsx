import {
  Image, Flex, Spacer, Heading, SimpleGrid
} from '@chakra-ui/react';


export function ImagePreview({originalImageData, processedImageData} : {originalImageData: any, processedImageData: any}): JSX.Element {
  return (
    <>
      <Flex color="white" rounded={15} alignContent="center" alignItems="center" height="100vh" width="100vw" direction="row">
        <Spacer/>
        <SimpleGrid justifyItems="center">
          <Heading fontFamily="Montserrat, sans-serif" fontSize="2.3em">Original Image</Heading>
          <Image width="calc(100vw / 2.3)" fit="fill" src={URL.createObjectURL(originalImageData)}></Image>
        </SimpleGrid>
        <Spacer/>
        <SimpleGrid justifyItems="center">
          <Heading fontFamily="Montserrat, sans-serif" fontSize="2.3em">Processed Image</Heading>
          <Image width="calc(100vw / 2.3)" fit="fill" src={URL.createObjectURL(processedImageData)}></Image>
        </SimpleGrid>
        <Spacer/>
      </Flex>
    </>
  )
}
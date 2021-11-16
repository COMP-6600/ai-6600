import {
  Collapse, Box, useDisclosure, Text, Center, Heading
} from '@chakra-ui/react';

// Adapted from https://chakra-ui.com/docs/components/transitions#collapse-transition
export function Status({status, detail, secondsElapsed, popOpen}: {status: string, detail: string, secondsElapsed: number, popOpen: boolean}): JSX.Element {
  const { isOpen } = useDisclosure({
    isOpen: popOpen
  })

  return (
    <>
      <Collapse in={isOpen} animateOpacity>
        <Center>
          <Box
            p="20px"
            width="calc(100vw / 5)"
            color="white"
            bg="blue.800"
            rounded="md"
            shadow="md"
            textAlign="center"
          >
            <Heading textTransform="capitalize">
              {status}
            </Heading>
            <Text textTransform="capitalize">
              {detail}
            </Text>
            <Text size="sm" color="gray">
              {secondsElapsed} seconds elapsed...
            </Text>
          </Box>
        </Center>
      </Collapse>
    </>
  )
}
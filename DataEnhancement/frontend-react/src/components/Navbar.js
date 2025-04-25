import React from 'react';
import { Box, Flex, Button, Heading, Spacer } from '@chakra-ui/react';

function Navbar() {
  return (
    <Box bg="blue.600" px={4} py={3}>
      <Flex maxW="container.xl" mx="auto" alignItems="center">
        <Heading size="md" color="white">LeadGen</Heading>
        <Spacer />
        <Button colorScheme="whiteAlpha" size="sm" mr={2}>Login</Button>
        <Button colorScheme="whiteAlpha" variant="outline" size="sm">Sign Up</Button>
      </Flex>
    </Box>
  );
}

export default Navbar;

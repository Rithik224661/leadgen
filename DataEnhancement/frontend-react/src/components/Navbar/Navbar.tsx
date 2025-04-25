import React from 'react';
import {
  Box,
  Flex,
  Button,
  useColorMode,
  useColorModeValue,
  Stack,
  Heading,
  IconButton,
  useDisclosure,
  HStack,
  Text,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon, HamburgerIcon, CloseIcon } from '@chakra-ui/icons';

interface NavLinkProps {
  children: React.ReactNode;
  href?: string;
}

const NavLink = ({ children, href = '#' }: NavLinkProps) => (
  <Box
    px={2}
    py={1}
    rounded={'md'}
    _hover={{
      textDecoration: 'none',
      bg: useColorModeValue('gray.200', 'gray.700'),
    }}
    cursor="pointer"
  >
    <Text>{children}</Text>
  </Box>
);

export default function Navbar() {
  const { colorMode, toggleColorMode } = useColorMode();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box bg={bg} px={4} borderBottom={1} borderStyle={'solid'} borderColor={borderColor}>
      <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
        <IconButton
          size={'md'}
          icon={isOpen ? <CloseIcon /> : <HamburgerIcon />}
          aria-label={'Open Menu'}
          display={{ md: 'none' }}
          onClick={isOpen ? onClose : onOpen}
        />
        <HStack spacing={8} alignItems={'center'}>
          <Heading size="md" color={useColorModeValue('brand.500', 'brand.200')}>
            LeadGen
          </Heading>
          <HStack as={'nav'} spacing={4} display={{ base: 'none', md: 'flex' }}>
            <NavLink>Dashboard</NavLink>
            <NavLink>Upload</NavLink>
            <NavLink>Tools</NavLink>
            <NavLink>Settings</NavLink>
          </HStack>
        </HStack>
        <Flex alignItems={'center'}>
          <Stack direction={'row'} spacing={7}>
            <Button onClick={toggleColorMode}>
              {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
            </Button>
          </Stack>
        </Flex>
      </Flex>

      {isOpen ? (
        <Box pb={4} display={{ md: 'none' }}>
          <Stack as={'nav'} spacing={4}>
            <NavLink>Dashboard</NavLink>
            <NavLink>Upload</NavLink>
            <NavLink>Tools</NavLink>
            <NavLink>Settings</NavLink>
          </Stack>
        </Box>
      ) : null}
    </Box>
  );
}

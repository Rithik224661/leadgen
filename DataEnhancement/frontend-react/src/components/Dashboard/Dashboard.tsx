import React from 'react';
import {
  Box,
  SimpleGrid,
  Text,
  VStack,
  useColorModeValue,
  Icon,
  Flex,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
} from '@chakra-ui/react';
import { FiUpload, FiDatabase, FiTool } from 'react-icons/fi';

interface StatsCardProps {
  title: string;
  stat: string;
  icon: React.ElementType;
  description?: string;
}

function StatsCard(props: StatsCardProps) {
  const { title, stat, icon, description } = props;
  const bgColor = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.200');

  return (
    <Stat
      px={{ base: 4, md: 8 }}
      py={5}
      bg={bgColor}
      shadow={'xl'}
      border={'1px solid'}
      borderColor={useColorModeValue('gray.200', 'gray.700')}
      rounded={'lg'}
    >
      <Flex justifyContent={'space-between'}>
        <Box pl={{ base: 2, md: 4 }}>
          <StatLabel fontWeight={'medium'} isTruncated>
            {title}
          </StatLabel>
          <StatNumber fontSize={'2xl'} fontWeight={'medium'}>
            {stat}
          </StatNumber>
          {description && (
            <StatHelpText color={textColor}>
              {description}
            </StatHelpText>
          )}
        </Box>
        <Box my={'auto'} color={useColorModeValue('gray.800', 'gray.200')} alignContent={'center'}>
          <Icon as={icon} w={8} h={8} />
        </Box>
      </Flex>
    </Stat>
  );
}

export default function Dashboard() {
  return (
    <Box maxW="7xl" mx={'auto'} pt={5} px={{ base: 2, sm: 12, md: 17 }}>
      <Text
        textAlign={'center'}
        fontSize={'4xl'}
        py={10}
        fontWeight={'bold'}
        color={useColorModeValue('gray.800', 'white')}
      >
        LeadGen Dashboard
      </Text>
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={{ base: 5, lg: 8 }}>
        <StatsCard
          title={'Files Processed'}
          stat={'50'}
          icon={FiUpload}
          description={'Last 30 days'}
        />
        <StatsCard
          title={'Data Points'}
          stat={'1,000'}
          icon={FiDatabase}
          description={'Total enriched entries'}
        />
        <StatsCard
          title={'Active Tools'}
          stat={'3'}
          icon={FiTool}
          description={'Scraping & Enhancement'}
        />
      </SimpleGrid>
    </Box>
  );
}

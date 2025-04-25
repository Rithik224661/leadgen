import React from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Text,
  VStack,
  HStack,
  Progress,
  useColorModeValue,
} from '@chakra-ui/react';
import { motion } from 'framer-motion';

interface DataPreviewProps {
  data: any[];
  columns: string[];
  isEnhancing: boolean;
  progress: number;
  onEnhance: () => void;
  onDownload: () => void;
}

export const DataPreview: React.FC<DataPreviewProps> = ({
  data,
  columns,
  isEnhancing,
  progress,
  onEnhance,
  onDownload,
}) => {
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <VStack spacing={4} align="stretch">
        <Box>
          <Text fontSize="xl" fontWeight="bold" mb={4}>
            Data Preview
          </Text>
          <HStack spacing={4} mb={4}>
            <Button
              colorScheme="blue"
              onClick={onEnhance}
              isDisabled={isEnhancing}
            >
              Enhance Data
            </Button>
            <Button
              variant="outline"
              onClick={onDownload}
              isDisabled={isEnhancing}
            >
              Download CSV
            </Button>
          </HStack>
          {isEnhancing && (
            <Box mb={4}>
              <Progress value={progress} size="sm" colorScheme="blue" mb={2} />
              <Text fontSize="sm" color="gray.500">
                Enhancing data... {Math.round(progress)}%
              </Text>
            </Box>
          )}
        </Box>

        <Box
          overflowX="auto"
          maxH="400px"
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="lg"
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                {columns.map((column) => (
                  <Th key={column}>{column}</Th>
                ))}
              </Tr>
            </Thead>
            <Tbody>
              {data.map((row, index) => (
                <Tr
                  key={index}
                  _hover={{ bg: hoverBg }}
                  transition="background-color 0.2s"
                >
                  {columns.map((column) => (
                    <Td key={`${index}-${column}`}>{row[column] || ''}</Td>
                  ))}
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </VStack>
    </motion.div>
  );
};

export default DataPreview;

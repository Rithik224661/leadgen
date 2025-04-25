import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Text,
  VStack,
  useColorModeValue,
  Button,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';


interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>;
  isProcessing: boolean;
  onRemove?: () => void;
}

export default function FileUpload({ onFileUpload, isProcessing, onRemove }: FileUploadProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    if (!file.name.endsWith('.csv')) {
      setError('Only CSV files are allowed');
      return;
    }

    setError(null);
    try {
      await onFileUpload(file);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 'Error uploading file';
      setError(errorMessage);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false
  });

  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.200');

  return (
    <VStack spacing={4} w="100%">
      <Box
        {...getRootProps()}
        w="100%"
        p={10}
        border="2px dashed"
        borderColor={isDragActive ? 'blue.400' : borderColor}
        borderRadius="lg"
        bg={bgColor}
        cursor="pointer"
        transition="all 0.2s"
        _hover={{ borderColor: 'blue.400' }}
      >
        <input {...getInputProps()} />
        <VStack spacing={2}>
          <Text color={textColor} textAlign="center">
            {isDragActive
              ? 'Drop the CSV file here'
              : 'Drag and drop a CSV file here, or click to select'}
          </Text>
          <Button size="sm" colorScheme="blue" variant="outline">
            Select File
          </Button>
        </VStack>
      </Box>

      {isProcessing && (
        <Box w="100%">
          <Progress size="sm" colorScheme="blue" isIndeterminate />
        </Box>
      )}

      {error && (
        <Alert status="error">
          <AlertIcon />
          <Box>
            <AlertTitle>Upload Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
      )}
    </VStack>
  );
}

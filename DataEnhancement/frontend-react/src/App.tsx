import React, { useState, useEffect } from 'react';
import { ChakraProvider, Box, VStack, Heading, Text, useToast, Button } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import axios, { AxiosResponse, AxiosError } from 'axios';
import theme from './theme/theme';
import Navbar from './components/Navbar/Navbar';
import Dashboard from './components/Dashboard/Dashboard';
import FileUpload from './components/FileUpload/FileUpload';
import Login from './components/Login/Login';

interface ApiResponse {
  message: string;
  total_processed?: number;
  filename?: string;
  results?: any[];
}

interface ApiError {
  message: string;
  error: string;
}

const queryClient = new QueryClient();

// Using proxy configuration from package.json

const App: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const toast = useToast();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleFileUpload = async (file: File): Promise<void> => {
    setIsProcessing(true);
    setCurrentFile(file);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication token not found. Please log in again.');
      }

      // Configure axios instance
      const axiosInstance = axios.create({
        timeout: 300000, // 5 minutes
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        withCredentials: true
      });
      
      console.log('Uploading file...');

      // Make the request
      const response = await axiosInstance.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
          console.log(`Upload Progress: ${percentCompleted}%`);
        }
      });

      toast({
        title: 'Success',
        description: `${response.data.message}. Processed ${response.data.total_processed} companies.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Reset the current file after successful upload
      setCurrentFile(null);
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      const errorMessage = axiosError.response?.data?.error || 
                          axiosError.message || 
                          'An error occurred while uploading the file';
      
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 8000,
        isClosable: true,
      });

      // Reset the current file on error
      setCurrentFile(null);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRemoveFile = (): void => {
    setCurrentFile(null);
  };

  const handleLoginSuccess = (token: string) => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider theme={theme}>
        <Box minH="100vh" py={10} px={4} bg="gray.50">
          {!isAuthenticated ? (
            <Login onLoginSuccess={handleLoginSuccess} />
          ) : (
            <VStack spacing={8} maxW="container.md" mx="auto">
              <Heading as="h1" size="xl" textAlign="center" color="gray.700">
                LeadGen Data Enhancement
              </Heading>
              <Text fontSize="lg" textAlign="center" color="gray.600">
                Upload your CSV file to enhance your data
              </Text>
              <Button onClick={handleLogout} alignSelf="flex-end">
                Logout
              </Button>
              <FileUpload
                onFileUpload={handleFileUpload}
                isProcessing={isProcessing}
                onRemove={currentFile ? handleRemoveFile : undefined}
              />
            </VStack>
          )}
        </Box>
      </ChakraProvider>
    </QueryClientProvider>
  );
};

export default App;

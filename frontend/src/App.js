import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import LiveRecorder from './components/LiveRecorder';

export default function App(){
  return (
    <Container maxWidth='md' sx={{py:4}}>
      <Typography variant='h4' gutterBottom>Speech Recognition — Live</Typography>
      <Box sx={{my:2}}>
        <LiveRecorder />
      </Box>
    </Container>
  );
}

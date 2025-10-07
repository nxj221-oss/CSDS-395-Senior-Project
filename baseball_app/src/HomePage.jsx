import * as React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

function HomePage() {
  return (
    <Box>
      <Typography variant="h3" sx={{ mb: 3 }} align="center">
        Welcome to MLB Prospects Dashboard
      </Typography>

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h5" sx={{ mb: 2 }}>
            Getting Started
          </Typography>
          <Typography variant="body1">
            MLB Prospects Homepage.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}

export default HomePage
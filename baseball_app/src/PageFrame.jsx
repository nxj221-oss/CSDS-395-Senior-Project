import { useState, useEffect } from 'react'

import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import SportsBaseballIcon from '@mui/icons-material/SportsBaseball';
import AboutDialog from './AboutDialog.jsx'

import { createTheme } from '@mui/material/styles';
import { red, blue } from '@mui/material/colors';

import './App.css'

const theme = createTheme({
  palette: {
    primary: {
      main: red[500],
    },
    secondary: {
      main: blue[500],
    },
  },
});

function PageFrame() {
  const [aboutOpen, setAboutOpen] = React.useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    fetch('/api/time').then(res => res.json()).then(data => {
      setCurrentTime(data.time);
    });
  }, []);

  const handleAboutOpen = () => {
    setAboutOpen(true);
  };

  const handleAboutClose = () => {
    setAboutOpen(false);
  };

  return (
    <>
        <Box sx={{ flexGrow: 1 }}>
      <AppBar theme={theme} >
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
          >
            <SportsBaseballIcon fontSize="large"/>
          </IconButton>
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, textAlign: "left" }}>
            MLB Prospects Predictive Analysis
          </Typography>
          <Button color="inherit" onClick={handleAboutOpen} >About This Project</Button>
        </Toolbar>
      </AppBar>
    </Box>
    {/* this time display is not necessary, it just serves as a model to show how we can get things from the backend */}
        <p>The current time is {new Date(currentTime * 1000).toLocaleString()}.</p>

        <AboutDialog open={aboutOpen} handleClose={handleAboutClose}/>
    </>
  )
}

export default PageFrame

import { useState, useEffect } from 'react';
import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import SportsBaseballIcon from '@mui/icons-material/SportsBaseball';
import AboutDialog from './AboutDialog.jsx';
import HomePage from './HomePage.jsx';
import MetricsPage from './MetricsPage.jsx';
import PredictionsPage from './PredictionsPage.jsx';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { red, blue } from '@mui/material/colors';
import './App.css';

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
  const [currentTab, setCurrentTab] = useState(0);

  const handleAboutOpen = () => {
    setAboutOpen(true);
  };

  const handleAboutClose = () => {
    setAboutOpen(false);
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <div>
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
            <Button color="inherit" onClick={handleAboutOpen}>About This Project</Button>
          </Toolbar>
          <Tabs 
            value={currentTab} 
            onChange={handleTabChange}
            textColor="inherit"
            indicatorColor="secondary"
            centered
          >
            <Tab label="Home" />
            <Tab label="Metrics" />
            <Tab label="Predictions" />
          </Tabs>
          </div>
        </AppBar>
      </Box>

      <Box sx={{ p: 3 }}>
        {currentTab === 0 && <HomePage />}
        {currentTab === 1 && <MetricsPage />}
        {currentTab === 2 && <PredictionsPage />}
      </Box>
      <AboutDialog open={aboutOpen} handleClose={handleAboutClose}/>
    </ThemeProvider>
  )
}

export default PageFrame

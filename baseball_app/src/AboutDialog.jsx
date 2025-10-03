import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import { createTheme } from '@mui/material/styles';
import { red, blue } from '@mui/material/colors';

import Slide from '@mui/material/Slide';

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

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

function AboutDialog(props) {

  return (
    <>
        <Dialog
        open={props.open}
        slots={{
          transition: Transition,
        }}
        keepMounted
        onClose={props.handleClose}
        aria-describedby="alert-dialog-slide-description"
      >
        <DialogTitle>{"ABOUT THIS PROJECT"}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-slide-description">
            Before MLB players reach the major leagues they spend time developing their own skills in the minor leagues. Evaluating minor leaguers effectively helps us predict who will become the future superstars in baseball before they reach those levels.
          </DialogContentText>
          <br />
          <DialogContentText>
            While there’s a lot of information to be gained based on how players in the minor leagues have performed in the past, the ways in which teams utilize their prospect players tells us how much a team believes in their own players.
          </DialogContentText>
          <br />
          <DialogContentText>
            When we combine a player’s performance with how that player is being utilized, it tells a story about both where a player is at right now and where they can be in the future.
          </DialogContentText>
          <br />
          <DialogContentText>
          The concept of cataloging and analyzing the careers of promising athletes is not new. Because of this, we have the opportunity to compare our results with these other sources to determine if our approach will have similar conclusions. As such, this project will include a comparison of our results with that of these other sources, including an analysis of any notable differences and the possible causes and limitations of our approach.
          </DialogContentText>
        </DialogContent>
        <DialogActions >
          <Button theme={theme} onClick={props.handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default AboutDialog

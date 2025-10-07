import * as React from 'react';
import { Box, Typography, Card, CardContent, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

function MetricsPage() {
  return (
    <Box>
      <Typography variant="h3" sx={{ mb: 2 }}>
        Model Performance Metrics
      </Typography>
      <Typography variant="body1" sx={{ color: 'white', mb: 4 }}>
        This page explains the evaluation metrics used for batters and pitchers in the player prediction model. Metrics include traditional stats, advanced analytics, and contextual usage data to assess current performance and project future value.
      </Typography>

      <Card>
        <CardContent>

          {/* Batter Data Accordion */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Batter Data Evaluations</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <ul>
                <li>
                  <strong>Traditional metrics:</strong> 
                  At-Bats (AB), Hits (H), Walks (BB), Home Runs (HR), Stolen Bases (SB), Batting Average (AVG), On-Base Percentage (OBP), Slugging Percentage (SLG), On-base Plus Slugging (OPS), Strikeout Rate (K%), etc. These measure raw offensive output and plate discipline.
                </li>
                <li>
                  <strong>Underlying data:</strong> 
                  Bat speed, contact rates, hard hit percentage (Hard Hit%). These advanced indicators reflect swing quality, power potential, and consistency—often used to predict future offensive performance even when traditional stats lag.
                </li>
              </ul>
            </AccordionDetails>
          </Accordion>

          {/* Pitcher Data Accordion */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Pitcher Data Evaluations</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <ul>
                <li>
                  <strong>Traditional metrics:</strong> 
                  Innings Pitched (IP), Strikeouts (K), Strikeout Rate (K%), Walk Rate (BB%), Earned Run Average (ERA), Walks + Hits per Inning Pitched (WHIP), Saves (SV), Holds (HD), Strikeout-to-Walk Differential (K-BB%), Batting Average Against (BAA), etc. These reflect effectiveness and efficiency.
                </li>
                <li>
                  <strong>Advanced metrics:</strong> 
                  Pitch velocity, pitch usage, spin rate (if available). These help gauge a pitcher's raw tools and potential, often used alongside results-based stats.
                </li>
              </ul>
            </AccordionDetails>
          </Accordion>

          {/* Batter Usage Accordion */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Batter Usage</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <ul>
                <li>
                  <strong>Positional use:</strong> 
                  Catcher (C), Shortstop (SS), and Center Field (CF) are premium defensive positions. Players at these positions are more valuable defensively, and offensive expectations may be lower.
                </li>
                <li>
                  <strong>Lineup spot:</strong> 
                  Batters in the 1–4 spots are generally higher-impact hitters. Players batting 8th or 9th may be valued more for defense or situational roles.
                </li>
              </ul>
            </AccordionDetails>
          </Accordion>

          {/* Pitcher Usage Accordion */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Pitcher Usage</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <ul>
                <li>
                  <strong>Role:</strong> 
                  Is the pitcher a starter or a reliever? Starters (SP) provide more innings; relievers may pitch in high-leverage situations.
                </li>
                <li>
                  <strong>Leverage & rotation placement:</strong> 
                  For relievers: closer, setup, or middle relief? For starters: SP1 (top of rotation) vs. SP5 (back-end). These roles reflect team trust and performance level.
                </li>
              </ul>
            </AccordionDetails>
          </Accordion>

          {/* Combined Factors Accordion */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Combined Contextual Factors</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <ul>
                <li>
                  <strong>Age vs. level:</strong> 
                  Younger players performing well at higher levels are strong indicators of future success.
                </li>
                <li>
                  <strong>Promotion frequency:</strong> 
                  Frequent promotions suggest strong development and trust from the organization.
                </li>
                <li>
                  <strong>Team context:</strong> 
                  On successful teams, it's harder to break into high-impact roles. Usage can be limited by roster depth, not just player ability.
                </li>
                <li>
                  <strong>Level weighting:</strong> 
                  Stats from the current level carry more weight, but prior performance is still considered to track growth or regression over time.
                </li>
              </ul>
            </AccordionDetails>
          </Accordion>

        </CardContent>
      </Card>
    </Box>
  );
}

export default MetricsPage
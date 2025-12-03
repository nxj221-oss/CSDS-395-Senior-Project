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
        This page explains the evaluation metrics used for batters in the player prediction model. Metrics include traditional stats, advanced analytics, and contextual usage data to assess current performance and project future value.
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
                  <strong>Handedness:</strong> 
                  Left-handed (L) batters are have a slight advantage over right-handed (R) batters, since they have a more advantageous matchup against the majority of right-handed pitchers. Switch hitters (S) are valued because they can bat from either side of the plate.
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
              </ul>
            </AccordionDetails>
          </Accordion>

        </CardContent>
      </Card>
    </Box>
  );
}

export default MetricsPage
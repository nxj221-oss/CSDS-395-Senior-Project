import * as React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';

const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'playerName', headerName: 'Player Name', width: 180 },
  { field: 'team', headerName: 'Team', width: 140 },
  { field: 'age', headerName: 'Age', width: 90 },
  { field: 'level', headerName: 'Level', width: 120 },
  { field: 'position', headerName: 'Position', width: 120 },
];

const rows = [
  {
    id: 1,
    playerName: 'Konnor Griffin',
    team: 'Pittsburg Pirates',
    age: 19,
    level: 'AA',
    position: 'SS',
  },
  {
    id: 2,
    playerName: 'Kevin McGonigle',
    team: 'Erie SeaWolves',
    age: 21,
    level: 'AA',
    position: 'SS',
  },
  {
    id: 3,
    playerName: 'Leo De Vries',
    team: 'Midland RockHounds',
    age: 18,
    level: 'AA',
    position: 'SS',
  },
  // Sample data for demo
];

function PredictionsPage() {
  return (
    <Box>
      <Typography variant="h3" sx={{ mb: 2 }}>
        Predictions Explorer
      </Typography>
      <Typography variant="body1" sx={{ color: 'white', mb: 4 }}>
        This page displays individual player predictions. You can filter, sort, and explore player-level data including team, age, and performance(HAS TO BE ADDED).
      </Typography>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ height: 500, width: '100%' }}>
            <DataGrid
              rows={rows}
              columns={columns}
              pageSize={10}
              rowsPerPageOptions={[5, 10, 25]}
              checkboxSelection
              disableSelectionOnClick
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default PredictionsPage
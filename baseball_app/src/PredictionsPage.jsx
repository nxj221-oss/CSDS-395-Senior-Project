import * as React from 'react';
import { Box, Typography, Card, CardContent, TextField, InputAdornment, IconButton, Stack, FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText, OutlinedInput } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import { DataGrid } from '@mui/x-data-grid';

const columns = [
  { field: 'Player', headerName: 'Player Name', width: 160 },
  { field: 'B', headerName: 'B', width: 50 },
  { field: 'Age', headerName: 'Age', width: 50 },
  { field: 'PO', headerName: 'PO', width: 50 },
  { field: 'PA', headerName: 'PA', width: 50 },
  { field: 'AB', headerName: 'At Bats', width: 70 },
  { field: 'R', headerName: 'R', width: 50 },
  { field: 'H', headerName: 'H', width: 50 },
  { field: '2B', headerName: '2B', width: 50 },
  { field: '3B', headerName: '3B', width: 50 },
  { field: 'HR', headerName: 'HR', width: 50 },
  { field: 'RBI', headerName: 'RBI', width: 50 },
  { field: 'BB', headerName: 'BB', width: 50 },
  { field: 'SO', headerName: 'SO', width: 50 },
  { field: 'SB', headerName: 'SB', width: 50 },
  { field: 'CS', headerName: 'CS', width: 50 },
  { field: '1B', headerName: '1B', width: 50 },
  { field: 'TB', headerName: 'TB', width: 50 },
  { field: 'AVG', headerName: 'AVG', width: 70 },
  { field: 'OBP', headerName: 'OBP', width: 70 },
  { field: 'SLG', headerName: 'SLG', width: 70 },
  { field: 'PerformanceMetric', headerName: 'Performance Metric', width: 120 },
  { field: 'UsageMetric', headerName: 'Usage Metric', width: 120 },
  { field: 'CombinedMetric', headerName: 'Combined Metric', width: 120 },
];

function PredictionsPage() {
  const [searchInput, setSearchInput] = React.useState('');
  const [debouncedSearch, setDebouncedSearch] = React.useState('');
  const [selectedTeams, setSelectedTeams] = React.useState([]);
  const [selectedAges, setSelectedAges] = React.useState([]);
  const [selectedLevels, setSelectedLevels] = React.useState([]);
  const [selectedPositions, setSelectedPositions] = React.useState([]);
  const [rows, setRows] = React.useState([]);

  React.useEffect(() => {
    const timeoutId = setTimeout(() => setDebouncedSearch(searchInput), 250);
    return () => clearTimeout(timeoutId);
  }, [searchInput]);

  React.useEffect(() => {
    fetch('/api/playerData').then(res => res.json()).then(data => {
      setRows(data);
    });
  }, []);

  const teamOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.PO))).sort(), [rows]);
  const ageOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.Age))).sort((a, b) => a - b), [rows]);
  const levelOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.B))).sort(), [rows]);
  const positionOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.HR))).sort(), [rows]);

  const filteredRows = React.useMemo(() => {
    const query = debouncedSearch.trim().toLowerCase();
    return rows.filter((r) => {
      const passesSearch = !query ||
        String(r.Player).toLowerCase().includes(query);
        //|| String(r.team).toLowerCase().includes(query);
      const passesTeam = selectedTeams.length === 0 || selectedTeams.includes(r.PO);
      const passesAge = selectedAges.length === 0 || selectedAges.includes(r.Age);
      const passesLevel = selectedLevels.length === 0 || selectedLevels.includes(r.B);
      const passesPosition = selectedPositions.length === 0 || selectedPositions.includes(r.HR);
      return passesSearch && passesTeam && passesAge && passesLevel && passesPosition;
    });
  }, [debouncedSearch, selectedTeams, selectedAges, selectedLevels, selectedPositions, rows]);

  return (
    <Box>
      <Typography variant="h3" sx={{ mb: 2 }}>
        Predictions Explorer
      </Typography>
      <Typography variant="body1" sx={{ color: 'white', mb: 4 }}>
        This page displays individual player predictions. You can filter, sort, and explore player-level data including team, age, and performance(HAS TO BE ADDED).
      </Typography>

      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        {/* Search Input Field */}
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Search by player name"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          sx={{ bgcolor: 'white' }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="clear search"
                  size="small"
                  onClick={() => setSearchInput('')}
                  edge="end"
                  disabled={!searchInput}
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        {/* Team Filter */}
        <FormControl sx={{ minWidth: 180 }} size="small">
          <InputLabel id="team-filter-label">PO</InputLabel>
          <Select
            labelId="team-filter-label"
            multiple
            value={selectedTeams}
            onChange={(e) => setSelectedTeams(e.target.value)}
            input={<OutlinedInput label="PO" />}
            renderValue={(selected) => selected.join(', ')}
            sx={{ bgcolor: 'white' }}
          >
            {teamOptions.map((name) => (
              <MenuItem key={name} value={name}>
                <Checkbox checked={selectedTeams.indexOf(name) > -1} />
                <ListItemText primary={name} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Age Filter */}
        <FormControl sx={{ minWidth: 140 }} size="small">
          <InputLabel id="age-filter-label">Age</InputLabel>
          <Select
            labelId="age-filter-label"
            multiple
            value={selectedAges}
            onChange={(e) => setSelectedAges(e.target.value)}
            input={<OutlinedInput label="Age" />}
            renderValue={(selected) => selected.join(', ')}
            sx={{ bgcolor: 'white' }}
          >
            {ageOptions.map((age) => (
              <MenuItem key={age} value={age}>
                <Checkbox checked={selectedAges.indexOf(age) > -1} />
                <ListItemText primary={String(age)} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Level Filter */}
        <FormControl sx={{ minWidth: 140 }} size="small">
          <InputLabel id="level-filter-label">B</InputLabel>
          <Select
            labelId="level-filter-label"
            multiple
            value={selectedLevels}
            onChange={(e) => setSelectedLevels(e.target.value)}
            input={<OutlinedInput label="B" />}
            renderValue={(selected) => selected.join(', ')}
            sx={{ bgcolor: 'white' }}
          >
            {levelOptions.map((level) => (
              <MenuItem key={level} value={level}>
                <Checkbox checked={selectedLevels.indexOf(level) > -1} />
                <ListItemText primary={level} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Position Filter */}
        <FormControl sx={{ minWidth: 160 }} size="small">
          <InputLabel id="position-filter-label">HR</InputLabel>
          <Select
            labelId="position-filter-label"
            multiple
            value={selectedPositions}
            onChange={(e) => setSelectedPositions(e.target.value)}
            input={<OutlinedInput label="HR" />}
            renderValue={(selected) => selected.join(', ')}
            sx={{ bgcolor: 'white' }}
          >
            {positionOptions.map((pos) => (
              <MenuItem key={pos} value={pos}>
                <Checkbox checked={selectedPositions.indexOf(pos) > -1} />
                <ListItemText primary={pos} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Stack>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ height: 500, width: '100%' }}>
            <DataGrid
              rows={filteredRows}
              columns={columns}
              getRowId={(row) => row.Player}
              pageSize={10}
              rowsPerPageOptions={[5, 10, 25]}
              checkboxSelection
              disableSelectionOnClick
            />
          </Box>
          {filteredRows.length === 0 && (
            <Typography variant="body2" sx={{ mt: 2 }}>
              No results match your search.
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default PredictionsPage
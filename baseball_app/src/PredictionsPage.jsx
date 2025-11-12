import * as React from 'react';
import { Box, Typography, Card, CardContent, TextField, InputAdornment, IconButton, Stack, FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText, OutlinedInput } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import { DataGrid } from '@mui/x-data-grid';

const columns = [
  { field: 'id', headerName: 'ID', width: 70 },
  { field: 'playerName', headerName: 'Player Name', width: 180 },
  { field: 'team', headerName: 'Team', width: 140 },
  { field: 'age', headerName: 'Age', width: 90 },
  { field: 'level', headerName: 'Level', width: 120 },
  { field: 'position', headerName: 'Position', width: 120 },
];

// const rows = [
//   {
//     id: 1,
//     playerName: 'Konnor Griffin',
//     team: 'Pittsburg Pirates',
//     age: 19,
//     level: 'AA',
//     position: 'SS',
//   },
//   {
//     id: 2,
//     playerName: 'Kevin McGonigle',
//     team: 'Erie SeaWolves',
//     age: 21,
//     level: 'AA',
//     position: 'SS',
//   },
//   {
//     id: 3,
//     playerName: 'Leo De Vries',
//     team: 'Midland RockHounds',
//     age: 18,
//     level: 'AA',
//     position: 'SS',
//   },
//   {
//     id: 4,
//     playerName: 'Josue Briceño',
//     team: 'Erie Seawolves',
//     age: 21,
//     level: 'AA',
//     position: '1B',
//   },
//   {
//     id: 5,
//     playerName: 'Travis Bazzana',
//     team: 'Columbus Clippers',
//     age: 23,
//     level: 'AAA',
//     position: '2B',
//   },
//   {
//     id: 6,
//     playerName: 'Alfredo Duno',
//     team: 'Daytona Tortugas',
//     age: 19,
//     level: 'A',
//     position: 'C',
//   },
//   {
//     id: 7,
//     playerName: 'Walker Jenkins',
//     team: 'St. Paul Saints',
//     age: 20,
//     level: 'AAA',
//     position: 'OF',
//   },
//   {
//     id: 8,
//     playerName: 'Eduardo Quintero',
//     team: 'Great Lakes Loons',
//     age: 20,
//     level: 'A+',
//     position: 'OF',
//   },
//   // Sample data for demo
// ];

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
    fetch('/api/examplePlayerData').then(res => res.json()).then(data => {
      setRows(data);
    });
  }, []);

  const teamOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.team))).sort(), [rows]);
  const ageOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.age))).sort((a, b) => a - b), [rows]);
  const levelOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.level))).sort(), [rows]);
  const positionOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.position))).sort(), [rows]);

  const filteredRows = React.useMemo(() => {
    const query = debouncedSearch.trim().toLowerCase();
    return rows.filter((r) => {
      const passesSearch = !query ||
        String(r.playerName).toLowerCase().includes(query) ||
        String(r.team).toLowerCase().includes(query);
      const passesTeam = selectedTeams.length === 0 || selectedTeams.includes(r.team);
      const passesAge = selectedAges.length === 0 || selectedAges.includes(r.age);
      const passesLevel = selectedLevels.length === 0 || selectedLevels.includes(r.level);
      const passesPosition = selectedPositions.length === 0 || selectedPositions.includes(r.position);
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
          placeholder="Search by player or team"
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
          <InputLabel id="team-filter-label">Team</InputLabel>
          <Select
            labelId="team-filter-label"
            multiple
            value={selectedTeams}
            onChange={(e) => setSelectedTeams(e.target.value)}
            input={<OutlinedInput label="Team" />}
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
          <InputLabel id="level-filter-label">Level</InputLabel>
          <Select
            labelId="level-filter-label"
            multiple
            value={selectedLevels}
            onChange={(e) => setSelectedLevels(e.target.value)}
            input={<OutlinedInput label="Level" />}
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
          <InputLabel id="position-filter-label">Position</InputLabel>
          <Select
            labelId="position-filter-label"
            multiple
            value={selectedPositions}
            onChange={(e) => setSelectedPositions(e.target.value)}
            input={<OutlinedInput label="Position" />}
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
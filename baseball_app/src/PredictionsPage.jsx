import * as React from 'react';
import { Box, Typography, Card, CardContent, TextField, InputAdornment, IconButton, Stack, FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText, OutlinedInput, Button, Dialog, DialogTitle, DialogContent } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import { DataGrid } from '@mui/x-data-grid';
import { BarChart, Bar, LineChart, Line, ScatterChart, Scatter, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const columns = [
  { field: 'rank', headerName: 'Rank', width: 50 },
  { field: 'Player', headerName: 'Player Name', width: 180 },
  { field: 'B', headerName: 'B', width: 70 },
  { field: 'Age', headerName: 'Age', width: 70 },
  { field: 'PO', headerName: 'PO', width: 70 },
  { field: 'AB', headerName: 'At Bats', width: 90 },
  { field: 'team', headerName: 'Team', width: 180},
  { field: 'level', headerName: 'Level', width: 70 },
  { field: 'perf', headerName: 'Performance', width: 120 },
  { field: 'use', headerName: 'Usage', width: 120 },
  { field: 'combined', headerName: 'Combined', width: 120 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B9D'];

function PredictionsPage() {
  const [searchInput, setSearchInput] = React.useState('');
  const [debouncedSearch, setDebouncedSearch] = React.useState('');
  const [selectedTeams, setSelectedTeams] = React.useState([]);
  const [selectedAges, setSelectedAges] = React.useState([]);
  const [selectedLevels, setSelectedLevels] = React.useState([]);
  const [selectedPositions, setSelectedPositions] = React.useState([]);
  const [rows, setRows] = React.useState([]);
  const [selectedRowIds, setSelectedRowIds] = React.useState([]);
  const [isCompareDialogOpen, setIsCompareDialogOpen] = React.useState(false);

  React.useEffect(() => {
    const timeoutId = setTimeout(() => setDebouncedSearch(searchInput), 250);
    return () => clearTimeout(timeoutId);
  }, [searchInput]);

  React.useEffect(() => {
    fetch('/api/playerData').then(res => res.json()).then(data => {
      setRows(data);
    });
  }, []);

  const teamOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.team))).filter(l => !l.includes('/')).sort(), [rows]);
  const ageOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.Age))).sort((a, b) => a - b), [rows]);
  const levelOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.level))).filter(l => !l.includes('/')).sort(), [rows]);
  const positionOptions = React.useMemo(() => Array.from(new Set(rows.map(r => r.PO))).sort(), [rows]);

  const filteredRows = React.useMemo(() => {
    const query = debouncedSearch.trim().toLowerCase();
    return rows.filter((r) => {
      const passesSearch = !query ||
        String(r.Player).toLowerCase().includes(query)
        || String(r.team).toLowerCase().includes(query);
      const passesTeam = selectedTeams.length === 0 || r.team.includes(selectedTeams);
      const passesAge = selectedAges.length === 0 || selectedAges.includes(r.Age);
      const passesLevel = selectedLevels.length === 0 || selectedLevels.includes(r.level);
      const passesPosition = selectedPositions.length === 0 || selectedPositions.includes(r.PO);
      return passesSearch && passesTeam && passesAge && passesLevel && passesPosition;
    });
  }, [debouncedSearch, selectedTeams, selectedAges, selectedLevels, selectedPositions, rows]);

  // Chart Data Calculations
  const ageDistribution = React.useMemo(() => {
    const ageCounts = {};
    filteredRows.forEach(row => {
      ageCounts[row.Age] = (ageCounts[row.Age] || 0) + 1;
    });
    return Object.entries(ageCounts)
      .map(([age, count]) => ({ age: Number(age), count }))
      .sort((a, b) => a.age - b.age);
  }, [filteredRows]);

  const teamDistribution = React.useMemo(() => {
    const teamCounts = {};
    filteredRows.forEach(row => {
      teamCounts[row.team] = (teamCounts[row.team] || 0) + 1;
    });
    return Object.entries(teamCounts)
      .map(([team, count]) => ({ team, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [filteredRows]);

  const positionDistribution = React.useMemo(() => {
    const posCounts = {};
    filteredRows.forEach(row => {
      posCounts[row.PO] = (posCounts[row.PO] || 0) + 1;
    });
    return Object.entries(posCounts)
      .map(([position, value]) => ({ position, value }))
      .sort((a, b) => b.value - a.value);
  }, [filteredRows]);

  const performanceByAge = React.useMemo(() => {
    const agePerf = {};
    filteredRows.forEach(row => {
      if (!agePerf[row.Age]) {
        agePerf[row.Age] = { total: 0, count: 0 };
      }
      agePerf[row.Age].total += parseFloat(row.perf) || 0;
      agePerf[row.Age].count += 1;
    });
    return Object.entries(agePerf)
      .map(([age, data]) => ({ 
        age: Number(age), 
        avgPerformance: data.total / data.count 
      }))
      .sort((a, b) => a.age - b.age);
  }, [filteredRows]);

  const performanceVsUsage = React.useMemo(() => {
    return filteredRows
      .filter(row => row.perf && row.use)
      .map(row => ({
        performance: parseFloat(row.perf),
        usage: parseFloat(row.use),
        player: row.Player
      }));
  }, [filteredRows]);

  const selectedPlayers = React.useMemo(
    () => rows.filter((row) => selectedRowIds.includes(row.Player)),
    [rows, selectedRowIds],
  );

  return (
    <Box>
      <Typography variant="h3" sx={{ mb: 2 }}>
        Predictions Explorer
      </Typography>
      <Typography variant="body1" sx={{ color: 'white', mb: 4 }}>
        This page displays individual player predictions. You can filter, sort, and explore player-level data including team, age, level, and performance.
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
            input={<OutlinedInput label="PO" />}
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

      {/* Compare Players Button */}
      <Box sx={{ mb: 2 }}>
        <Button
          variant="contained"
          color="error"
          disabled={selectedRowIds.length <= 1}
          onClick={() => setIsCompareDialogOpen(true)}
          sx={{
            bgcolor: 'primary.main',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
            '&.Mui-disabled': {
              bgcolor: 'rgba(255, 255, 255, 0.25)',
              color: 'rgba(255, 255, 255, 0.6)',
            },
          }}
        >
          Compare Players
        </Button>
      </Box>
      <Dialog
        open={isCompareDialogOpen}
        onClose={() => setIsCompareDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>Compare Players</DialogTitle>
        <DialogContent dividers>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 1 }}>
            {selectedPlayers.map((player) => (
              <Card key={player.Player} sx={{ minWidth: 220, flex: 1 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {player.Player}
                  </Typography>
                  <Typography variant="body2">Team: {player.team}</Typography>
                  <Typography variant="body2">Level: {player.level}</Typography>
                  <Typography variant="body2">Age: {player.Age}</Typography>
                  <Typography variant="body2">Position: {player.PO}</Typography>
                  <Typography variant="body2">AB: {player.AB}</Typography>
                  <Typography variant="body2">Performance: {player.perf}</Typography>
                  <Typography variant="body2">Usage: {player.use}</Typography>
                  <Typography variant="body2">Combined: {player.combined}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        </DialogContent>
      </Dialog>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ height: 500, width: '100%' }}>
            <DataGrid
              rows={filteredRows}
              columns={columns}
              getRowId={(row) => row.Player}
              onRowSelectionModelChange={(newSelection) => {
                if (Array.isArray(newSelection)) {
                  setSelectedRowIds(newSelection);
                } else if (newSelection && Array.isArray(newSelection.ids)) {
                  setSelectedRowIds(newSelection.ids);
                } else if (newSelection && newSelection.ids && typeof newSelection.ids.forEach === 'function') {
                  const ids = [];
                  newSelection.ids.forEach((id) => ids.push(id));
                  setSelectedRowIds(ids);
                } else {
                  setSelectedRowIds([]);
                }
              }}
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

      {/* Visualizations Section */}
      <Typography variant="h4" sx={{ mt: 5, mb: 3 }}>
        Data Visualizations
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Age Distribution */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Age Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ageDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="age" label={{ value: 'Age', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Bar dataKey="count" fill="#0088FE" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Position Distribution */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Position Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={positionDistribution}
                  dataKey="value"
                  nameKey="position"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => entry.position}
                >
                  {positionDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Average Performance by Age */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Average Performance by Age
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceByAge}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="age" label={{ value: 'Age', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Avg Performance', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="avgPerformance" stroke="#8884D8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance vs Usage Scatter Plot */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance vs Usage
            </Typography>
            <ResponsiveContainer width="100%" height={350}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="usage" name="Usage" label={{ value: 'Usage', position: 'insideBottom', offset: -5 }} />
                <YAxis dataKey="performance" name="Performance" label={{ value: 'Performance', angle: -90, position: 'insideLeft' }} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter data={performanceVsUsage} fill="#FF8042" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}

export default PredictionsPage
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

// Consolidated production-grade fetch
export const fetchDashboardSummary = createAsyncThunk(
    'dashboard/fetchSummary',
    async (_, { getState, rejectWithValue }) => {
        const { dashboard } = getState();
        const now = Date.now();
        const lastFetched = dashboard.lastFetched ? new Date(dashboard.lastFetched).getTime() : 0;
        
        // Prevent re-fetching if data is less than 60 seconds old
        if (dashboard.summary && (now - lastFetched < 60000)) {
            return dashboard.summary;
        }

        const response = await api.get('/api/dashboard/summary');
        return response.data;
    }
);

const dashboardSlice = createSlice({
    name: 'dashboard',
    initialState: {
        summary: null,
        loading: false,
        error: null,
        lastFetched: null
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchDashboardSummary.pending, (state) => {
                state.loading = true;
            })
            .addCase(fetchDashboardSummary.fulfilled, (state, action) => {
                state.loading = false;
                state.summary = action.payload;
                state.lastFetched = new Date().toISOString();
            })
            .addCase(fetchDashboardSummary.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message;
            });
    },
});

export default dashboardSlice.reducer;

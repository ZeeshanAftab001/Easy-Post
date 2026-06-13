import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

export const fetchAccounts = createAsyncThunk('accounts/fetchAccounts', async () => {
    const response = await api.get('/api/oauth/accounts/');
    return response.data;
});

const accountSlice = createSlice({
    name: 'accounts',
    initialState: {
        list: [],
        connectedCount: 0,
        loading: false,
        error: null,
    },
    reducers: {
        updateAccountStatus: (state, action) => {
            const { id, is_active } = action.payload;
            const account = state.list.find(a => a.id === id);
            if (account) {
                account.is_active = is_active;
            }
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchAccounts.pending, (state) => {
                state.loading = true;
            })
            .addCase(fetchAccounts.fulfilled, (state, action) => {
                state.loading = false;
                state.list = action.payload;
                state.connectedCount = action.payload.filter(a => a.is_active).length;
            })
            .addCase(fetchAccounts.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message;
            });
    },
});

export const { updateAccountStatus } = accountSlice.actions;
export default accountSlice.reducer;

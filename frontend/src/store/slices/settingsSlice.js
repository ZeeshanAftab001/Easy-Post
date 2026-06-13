import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

export const fetchKnowledgeBase = createAsyncThunk('settings/fetchKnowledge', async () => {
  const response = await api.get('/api/ai/knowledge/');
  return response.data;
});

export const updateProfileField = createAsyncThunk('settings/updateProfile', async (updateData) => {
  const response = await api.patch('/api/users/me', updateData);
  return response.data;
});

const settingsSlice = createSlice({
  name: 'settings',
  initialState: {
    knowledgeBase: [],
    combinedKnowledge: '',
    status: '',
    loading: false,
    error: null,
  },
  reducers: {
    setStatus: (state, action) => {
      state.status = action.payload;
    },
    clearStatus: (state) => {
      state.status = '';
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchKnowledgeBase.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchKnowledgeBase.fulfilled, (state, action) => {
        state.loading = false;
        state.knowledgeBase = action.payload;
        state.combinedKnowledge = action.payload.map(k => k.content).join('\n\n---\n\n');
      })
      .addCase(fetchKnowledgeBase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(updateProfileField.pending, (state) => {
          state.status = 'Syncing...';
      })
      .addCase(updateProfileField.fulfilled, (state) => {
          state.status = 'System Updated.';
      })
      .addCase(updateProfileField.rejected, (state) => {
          state.status = 'Sync Failed.';
      });
  },
});

export const { setStatus, clearStatus } = settingsSlice.actions;
export default settingsSlice.reducer;

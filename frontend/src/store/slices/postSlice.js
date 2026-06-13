import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api';

export const fetchPosts = createAsyncThunk('posts/fetchPosts', async () => {
    const response = await api.get('/api/posts/');
    return response.data;
});

export const fetchAnalytics = createAsyncThunk('posts/fetchAnalytics', async () => {
    const response = await api.get('/api/posts/analytics/');
    return response.data;
});

const postSlice = createSlice({
    name: 'posts',
    initialState: {
        list: [],
        analytics: { summary: {}, trends: [] },
        loading: false,
        error: null,
    },
    reducers: {
        addPost: (state, action) => {
            state.list.unshift(action.payload);
        },
        removePost: (state, action) => {
            state.list = state.list.filter(p => p.id !== action.payload);
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchPosts.pending, (state) => {
                state.loading = true;
            })
            .addCase(fetchPosts.fulfilled, (state, action) => {
                state.loading = false;
                state.list = action.payload;
            })
            .addCase(fetchPosts.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message;
            })
            .addCase(fetchAnalytics.fulfilled, (state, action) => {
                state.analytics = action.payload;
            });
    },
});

export const { addPost, removePost } = postSlice.actions;
export default postSlice.reducer;

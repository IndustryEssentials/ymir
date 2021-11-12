import { Effect, Reducer, Subscription } from 'umi';

const WatchRoute = {
  name: 'watchRoute',
  state: {
    current: '/portal',
  },
  effects: {
    *updateRoute({ payload }, { put }) {
      //    console.log('effect--updateRoute', payload)
      put({
        type: 'UPDATEROUTE',
        payload,
      });
    },
  },
  reducers: {
    UPDATEROUTE(state, { payload }) {
      // console.log('STATE,',state, payload)
      return {
        ...state,
        current: payload,
      };
    },
  },
  subscriptions: {
    setup({ dispatch, history }) {
      return history.listen(({ pathname, query }) => {
        dispatch({
          type: 'UPDATEROUTE',
          payload: pathname,
        });
      });
    },
  },
};

export default WatchRoute;

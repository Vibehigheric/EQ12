let State = {
  session: '',
  user: undefined,
  popupClips: [],
};

export const getState = () => {
  return State;
}

export const setState = (newState) => {
  State = {
    ...State,
    ...newState,
  };
}
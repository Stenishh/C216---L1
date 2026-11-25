import { useCallback, useEffect, useState } from "react";

export function useResource(load, params = {}) {
  const path = JSON.stringify(params);
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({
    path: null,
    data: null,
    loading: true,
    error: "",
  });
  const reload = useCallback(() => setRevision((value) => value + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setState({ load, path, revision, data: null, loading: true, error: "" });
    load(JSON.parse(path), { signal: controller.signal }).then(
      (data) => {
        if (active)
          setState({ load, path, revision, data, loading: false, error: "" });
      },
      (error) => {
        if (active && error.name !== "AbortError")
          setState({
            load,
            path,
            revision,
            data: null,
            loading: false,
            error: error.message,
          });
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, [load, path, revision]);
  return {
    ...(state.load === load &&
    state.path === path &&
    state.revision === revision
      ? state
      : { data: null, loading: true, error: "" }),
    reload,
  };
}

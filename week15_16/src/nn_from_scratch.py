"""Reusable NumPy neural network (Week 15-16). Used by notebook 04."""
import numpy as np


# ---------- activations ----------
def sigmoid(z):  return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
def relu(z):     return np.maximum(0, z)
def tanh(z):     return np.tanh(z)

ACT = {
    "sigmoid": (sigmoid, lambda a: a * (1 - a)),          # derivative from output a
    "relu":    (relu,    lambda a: (a > 0).astype(float)),
    "tanh":    (tanh,    lambda a: 1 - a ** 2),
}


# ---------- loss ----------
def bce(y, p, eps=1e-12):
    p = np.clip(p, eps, 1 - eps)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))


# ---------- optimizers ----------
class SGD:
    def __init__(self, lr=0.1): self.lr = lr
    def step(self, params, grads):
        for k in params: params[k] -= self.lr * grads[k]


class Adam:
    def __init__(self, lr=0.01, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps = lr, b1, b2, eps
        self.m, self.v, self.t = {}, {}, 0
    def step(self, params, grads):
        self.t += 1
        for k in params:
            self.m.setdefault(k, np.zeros_like(params[k]))
            self.v.setdefault(k, np.zeros_like(params[k]))
            self.m[k] = self.b1 * self.m[k] + (1 - self.b1) * grads[k]
            self.v[k] = self.b2 * self.v[k] + (1 - self.b2) * grads[k] ** 2
            m_hat = self.m[k] / (1 - self.b1 ** self.t)
            v_hat = self.v[k] / (1 - self.b2 ** self.t)
            params[k] -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


# ---------- network ----------
class NeuralNetwork:
    """Fully connected net for binary classification.
    layer_sizes e.g. [2, 8, 8, 1]; hidden activation configurable, output sigmoid."""

    def __init__(self, layer_sizes, hidden_act="relu", seed=0):
        rng = np.random.default_rng(seed)
        self.sizes, self.act_name = layer_sizes, hidden_act
        self.params = {}
        for i in range(1, len(layer_sizes)):
            fan_in = layer_sizes[i - 1]
            scale = np.sqrt(2 / fan_in) if hidden_act == "relu" else np.sqrt(1 / fan_in)  # He / Xavier
            self.params[f"W{i}"] = rng.normal(0, scale, (fan_in, layer_sizes[i]))
            self.params[f"b{i}"] = np.zeros((1, layer_sizes[i]))

    def forward(self, X):
        act, _ = ACT[self.act_name]
        self.cache = {"A0": X}
        A, L = X, len(self.sizes) - 1
        for i in range(1, L + 1):
            Z = A @ self.params[f"W{i}"] + self.params[f"b{i}"]
            A = sigmoid(Z) if i == L else act(Z)
            self.cache[f"A{i}"] = A
        return A

    def backward(self, y):
        _, dact = ACT[self.act_name]
        y = y.reshape(-1, 1); m = y.shape[0]; L = len(self.sizes) - 1
        grads = {}
        dZ = self.cache[f"A{L}"] - y                      # sigmoid + BCE simplification
        for i in range(L, 0, -1):
            grads[f"W{i}"] = self.cache[f"A{i-1}"].T @ dZ / m
            grads[f"b{i}"] = dZ.sum(axis=0, keepdims=True) / m
            if i > 1:
                dZ = (dZ @ self.params[f"W{i}"].T) * dact(self.cache[f"A{i-1}"])
        return grads

    def fit(self, X, y, optimizer, epochs=500, batch_size=None, verbose=100, seed=0):
        rng = np.random.default_rng(seed)
        history, n = [], len(X)
        for ep in range(1, epochs + 1):
            idx = rng.permutation(n)
            bs = batch_size or n
            for s in range(0, n, bs):
                b = idx[s:s + bs]
                self.forward(X[b])
                optimizer.step(self.params, self.backward(y[b]))
            loss = bce(y.reshape(-1, 1), self.forward(X))
            history.append(loss)
            if verbose and ep % verbose == 0:
                print(f"epoch {ep:4d}  loss {loss:.4f}")
        return history

    def predict_proba(self, X): return self.forward(X)
    def predict(self, X):       return (self.forward(X) >= 0.5).astype(int).ravel()

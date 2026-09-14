#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

#define BIDI_L   0
#define BIDI_R   1
#define BIDI_AL  2
#define BIDI_ON  3
#define BIDI_NSM 4
#define BIDI_EN  5
#define BIDI_CS  6
#define BIDI_ES  7
#define BIDI_ET  8
#define BIDI_WS  9

static int normalized_class(int code) {
    if (code == BIDI_AL) return BIDI_R;
    if (code == BIDI_EN) return BIDI_L;
    if (code == BIDI_CS || code == BIDI_ES || code == BIDI_ET || code == BIDI_WS) return BIDI_ON;
    return code;
}

static PyObject *py_visual_order(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *classes_obj = NULL;
    if (!PyArg_ParseTuple(args, "O:visual_order", &classes_obj)) return NULL;

    PyObject *seq = PySequence_Fast(classes_obj, "classes must be a sequence of bidi class codes");
    if (seq == NULL) return NULL;
    Py_ssize_t length = PySequence_Fast_GET_SIZE(seq);

    int *resolved = NULL;
    int *levels = NULL;
    Py_ssize_t *order = NULL;
    if (length > 0) {
        resolved = PyMem_Malloc((size_t)length * sizeof(int));
        levels = PyMem_Malloc((size_t)length * sizeof(int));
        order = PyMem_Malloc((size_t)length * sizeof(Py_ssize_t));
        if (resolved == NULL || levels == NULL || order == NULL) {
            PyMem_Free(resolved);
            PyMem_Free(levels);
            PyMem_Free(order);
            Py_DECREF(seq);
            return PyErr_NoMemory();
        }
    }

    for (Py_ssize_t i = 0; i < length; ++i) {
        long code = PyLong_AsLong(PySequence_Fast_GET_ITEM(seq, i));
        if (PyErr_Occurred()) goto fail;
        if (code < BIDI_L || code > BIDI_WS) {
            PyErr_SetString(PyExc_ValueError, "unsupported bidi class code");
            goto fail;
        }
        resolved[i] = normalized_class((int)code);
        order[i] = i;
    }

    int paragraph_direction = BIDI_L;
    for (Py_ssize_t i = 0; i < length; ++i) {
        if (resolved[i] == BIDI_L || resolved[i] == BIDI_R) {
            paragraph_direction = resolved[i];
            break;
        }
    }
    int paragraph_level = paragraph_direction == BIDI_L ? 0 : 1;

    int previous = paragraph_direction;
    for (Py_ssize_t i = 0; i < length; ++i) {
        if (resolved[i] == BIDI_NSM) resolved[i] = previous;
        previous = resolved[i];
    }

    Py_ssize_t index = 0;
    while (index < length) {
        if (resolved[index] != BIDI_ON) {
            index += 1;
            continue;
        }
        Py_ssize_t end = index + 1;
        while (end < length && resolved[end] == BIDI_ON) end += 1;

        int before = paragraph_direction;
        for (Py_ssize_t prior = index; prior-- > 0;) {
            if (resolved[prior] == BIDI_L || resolved[prior] == BIDI_R) {
                before = resolved[prior];
                break;
            }
        }
        int after = paragraph_direction;
        for (Py_ssize_t following = end; following < length; ++following) {
            if (resolved[following] == BIDI_L || resolved[following] == BIDI_R) {
                after = resolved[following];
                break;
            }
        }
        int direction = before == after ? before : paragraph_direction;
        for (Py_ssize_t i = index; i < end; ++i) resolved[i] = direction;
        index = end;
    }

    int max_level = paragraph_level;
    int min_odd = -1;
    for (Py_ssize_t i = 0; i < length; ++i) {
        levels[i] = resolved[i] == paragraph_direction ? paragraph_level : paragraph_level + 1;
        if (levels[i] > max_level) max_level = levels[i];
        if ((levels[i] & 1) && (min_odd < 0 || levels[i] < min_odd)) min_odd = levels[i];
    }

    if (min_odd >= 0) {
        for (int level = max_level; level >= min_odd; --level) {
            Py_ssize_t start = 0;
            while (start < length) {
                if (levels[order[start]] < level) {
                    start += 1;
                    continue;
                }
                Py_ssize_t end = start + 1;
                while (end < length && levels[order[end]] >= level) end += 1;
                for (Py_ssize_t left = start, right = end - 1; left < right; ++left, --right) {
                    Py_ssize_t tmp = order[left];
                    order[left] = order[right];
                    order[right] = tmp;
                }
                start = end;
            }
        }
    }

    PyObject *order_tuple = PyTuple_New(length);
    PyObject *levels_tuple = PyTuple_New(length);
    if (order_tuple == NULL || levels_tuple == NULL) {
        Py_XDECREF(order_tuple);
        Py_XDECREF(levels_tuple);
        goto fail;
    }
    for (Py_ssize_t i = 0; i < length; ++i) {
        PyObject *order_value = PyLong_FromSsize_t(order[i]);
        PyObject *level_value = PyLong_FromLong(levels[i]);
        if (order_value == NULL || level_value == NULL) {
            Py_XDECREF(order_value);
            Py_XDECREF(level_value);
            Py_DECREF(order_tuple);
            Py_DECREF(levels_tuple);
            goto fail;
        }
        PyTuple_SET_ITEM(order_tuple, i, order_value);
        PyTuple_SET_ITEM(levels_tuple, i, level_value);
    }

    PyObject *result = PyTuple_Pack(2, order_tuple, levels_tuple);
    Py_DECREF(order_tuple);
    Py_DECREF(levels_tuple);
    PyMem_Free(resolved);
    PyMem_Free(levels);
    PyMem_Free(order);
    Py_DECREF(seq);
    return result;

fail:
    PyMem_Free(resolved);
    PyMem_Free(levels);
    PyMem_Free(order);
    Py_DECREF(seq);
    return NULL;
}

static PyMethodDef methods[] = {
    {"visual_order", py_visual_order, METH_VARARGS, "Resolve exact-surface bidi levels and visual permutation."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_azuzaley_kernel",
    "Compiled Azuzaley exact-layout index kernel.",
    -1,
    methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit__azuzaley_kernel(void) {
    return PyModule_Create(&module);
}

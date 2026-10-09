#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

static PyObject *py_walk_aeternum(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *period_obj = NULL;
    PyObject *speaking_obj = NULL;
    PyObject *start_obj = NULL;
    PyObject *step_obj = NULL;
    PyObject *count_obj = NULL;
    PyObject *limit_obj = NULL;
    if (!PyArg_ParseTuple(
            args,
            "OOOOOO:walk_aeternum",
            &period_obj,
            &speaking_obj,
            &start_obj,
            &step_obj,
            &count_obj,
            &limit_obj)) {
        return NULL;
    }

    PyObject *period_seq = PySequence_Fast(period_obj, "period must be a sequence of source positions");
    if (period_seq == NULL) return NULL;
    Py_ssize_t period_len = PySequence_Fast_GET_SIZE(period_seq);
    if (period_len <= 0) {
        PyErr_SetString(PyExc_ValueError, "period must be non-empty");
        Py_DECREF(period_seq);
        return NULL;
    }

    Py_buffer speaking;
    if (PyObject_GetBuffer(speaking_obj, &speaking, PyBUF_CONTIG_RO) < 0) {
        Py_DECREF(period_seq);
        return NULL;
    }
    if (speaking.len <= 0) {
        PyErr_SetString(PyExc_ValueError, "speaking mask must be non-empty");
        PyBuffer_Release(&speaking);
        Py_DECREF(period_seq);
        return NULL;
    }

    long long start = PyLong_AsLongLong(start_obj);
    if (PyErr_Occurred()) goto fail;
    long long step = PyLong_AsLongLong(step_obj);
    if (PyErr_Occurred()) goto fail;
    Py_ssize_t required = PyLong_AsSsize_t(count_obj);
    if (PyErr_Occurred()) goto fail;
    Py_ssize_t limit = PyLong_AsSsize_t(limit_obj);
    if (PyErr_Occurred()) goto fail;
    if ((step != -1 && step != 1) || required < 0 || limit < 0) {
        PyErr_SetString(PyExc_ValueError, "invalid Aeternum walk parameters");
        goto fail;
    }

    Py_ssize_t *period = PyMem_Malloc((size_t)period_len * sizeof(Py_ssize_t));
    if (period == NULL) {
        PyErr_NoMemory();
        goto fail;
    }
    for (Py_ssize_t i = 0; i < period_len; ++i) {
        Py_ssize_t value = PyLong_AsSsize_t(PySequence_Fast_GET_ITEM(period_seq, i));
        if (PyErr_Occurred()) {
            PyMem_Free(period);
            goto fail;
        }
        if (value < 0 || value >= speaking.len) {
            PyErr_SetString(PyExc_ValueError, "period source position lies outside speaking mask");
            PyMem_Free(period);
            goto fail;
        }
        period[i] = value;
    }

    Py_ssize_t *visited = NULL;
    if (limit > 0) {
        visited = PyMem_Malloc((size_t)limit * sizeof(Py_ssize_t));
        if (visited == NULL) {
            PyMem_Free(period);
            PyErr_NoMemory();
            goto fail;
        }
    }

    const unsigned char *mask = (const unsigned char *)speaking.buf;
    Py_ssize_t produced = 0;
    Py_ssize_t speaking_seen = 0;
    int completed = required == 0;

    Py_BEGIN_ALLOW_THREADS
    for (Py_ssize_t offset = 0; offset < limit && !completed; ++offset) {
        long long virtual_position = start + step * (long long)offset;
        long long phase = virtual_position % (long long)period_len;
        if (phase < 0) phase += (long long)period_len;
        Py_ssize_t source_position = period[(Py_ssize_t)phase];
        visited[produced++] = source_position;
        if (mask[source_position]) {
            speaking_seen += 1;
            if (speaking_seen == required) completed = 1;
        }
    }
    Py_END_ALLOW_THREADS

    PyObject *positions = PyTuple_New(produced);
    if (positions == NULL) {
        PyMem_Free(visited);
        PyMem_Free(period);
        goto fail;
    }
    for (Py_ssize_t i = 0; i < produced; ++i) {
        PyObject *value = PyLong_FromSsize_t(visited[i]);
        if (value == NULL) {
            Py_DECREF(positions);
            PyMem_Free(visited);
            PyMem_Free(period);
            goto fail;
        }
        PyTuple_SET_ITEM(positions, i, value);
    }
    PyMem_Free(visited);
    PyMem_Free(period);

    PyObject *result = PyTuple_New(2);
    if (result == NULL) {
        Py_DECREF(positions);
        goto fail;
    }
    PyTuple_SET_ITEM(result, 0, positions);
    Py_INCREF(completed ? Py_True : Py_False);
    PyTuple_SET_ITEM(result, 1, completed ? Py_True : Py_False);

    PyBuffer_Release(&speaking);
    Py_DECREF(period_seq);
    return result;

fail:
    PyBuffer_Release(&speaking);
    Py_DECREF(period_seq);
    return NULL;
}

static PyMethodDef methods[] = {
    {"walk_aeternum", py_walk_aeternum, METH_VARARGS, "Walk one periodic Aeternum source-position field."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_sydonic_kernel",
    "Compiled Sydonic Aeternum index kernel.",
    -1,
    methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit__sydonic_kernel(void) {
    return PyModule_Create(&module);
}

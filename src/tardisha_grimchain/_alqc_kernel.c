#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

#define LANE_COUNT 12
#define TOTAL_CAPACITY 144
#define SATURATION_LIMIT 110
#define MASK64 UINT64_MAX

static inline uint64_t rotl64(uint64_t value, unsigned int shift) {
    shift &= 63U;
    return shift ? ((value << shift) | (value >> (64U - shift))) : value;
}

static int read_u64_sequence(PyObject *obj, uint64_t out[LANE_COUNT], const char *name) {
    PyObject *seq = PySequence_Fast(obj, name);
    if (seq == NULL) return -1;
    if (PySequence_Fast_GET_SIZE(seq) != LANE_COUNT) {
        PyErr_Format(PyExc_ValueError, "%s must contain exactly 12 integers", name);
        Py_DECREF(seq);
        return -1;
    }
    for (Py_ssize_t i = 0; i < LANE_COUNT; ++i) {
        PyObject *item = PySequence_Fast_GET_ITEM(seq, i);
        unsigned long long value = PyLong_AsUnsignedLongLongMask(item);
        if (PyErr_Occurred()) {
            Py_DECREF(seq);
            return -1;
        }
        out[i] = (uint64_t)value;
    }
    Py_DECREF(seq);
    return 0;
}

static void round_lanes(
    uint64_t lanes[LANE_COUNT],
    uint64_t marker,
    const uint64_t q_mixes[LANE_COUNT],
    const uint64_t q_sums[LANE_COUNT]
) {
    uint64_t previous = lanes[LANE_COUNT - 1];
    for (uint64_t index = 0; index < LANE_COUNT; ++index) {
        uint64_t partner_index = (
            index * 7ULL + marker + (lanes[(index + 5ULL) % LANE_COUNT] & 0xFFULL)
        ) % LANE_COUNT;
        uint64_t load = 12ULL * index + partner_index;
        uint64_t identity_court = 13ULL * index;
        uint64_t flow = ((identity_court + load) % TOTAL_CAPACITY) < SATURATION_LIMIT ? 1ULL : 0ULL;
        uint64_t pressure = (load + 1ULL) * UINT64_C(0x0101010101010101);
        uint64_t current = lanes[index];
        uint64_t neighbor = lanes[(index + 1ULL) % LANE_COUNT];
        uint64_t folded = current
            ^ rotl64(previous, (unsigned int)((index + marker) % 64ULL))
            ^ rotl64(neighbor, (unsigned int)((load % 63ULL) + 1ULL));
        folded = folded + pressure + q_mixes[index] + marker + flow * TOTAL_CAPACITY;
        lanes[index] = rotl64(
            folded,
            (unsigned int)(((load + q_sums[index] + marker) % 63ULL) + 1ULL)
        );
        previous = current;
    }
}

static PyObject *py_absorb_raw(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *lanes_obj = NULL;
    PyObject *position_obj = NULL;
    PyObject *data_obj = NULL;
    PyObject *initial_obj = NULL;
    PyObject *q_mixes_obj = NULL;
    PyObject *q_sums_obj = NULL;
    if (!PyArg_ParseTuple(
            args, "OOOOOO:absorb_raw",
            &lanes_obj, &position_obj, &data_obj, &initial_obj, &q_mixes_obj, &q_sums_obj)) {
        return NULL;
    }

    uint64_t lanes[LANE_COUNT], initial[LANE_COUNT], q_mixes[LANE_COUNT], q_sums[LANE_COUNT];
    if (read_u64_sequence(lanes_obj, lanes, "lanes") < 0
            || read_u64_sequence(initial_obj, initial, "initial_lanes") < 0
            || read_u64_sequence(q_mixes_obj, q_mixes, "q_mixes") < 0
            || read_u64_sequence(q_sums_obj, q_sums, "q_sums") < 0) {
        return NULL;
    }

    unsigned long long position_value = PyLong_AsUnsignedLongLong(position_obj);
    if (PyErr_Occurred()) return NULL;
    uint64_t position = (uint64_t)position_value;

    Py_buffer view;
    if (PyObject_GetBuffer(data_obj, &view, PyBUF_CONTIG_RO) < 0) return NULL;
    const unsigned char *data = (const unsigned char *)view.buf;

    Py_BEGIN_ALLOW_THREADS
    for (Py_ssize_t offset = 0; offset < view.len; ++offset) {
        uint64_t byte = (uint64_t)data[offset];
        uint64_t lane = position % LANE_COUNT;
        uint64_t partner_index = (byte + position) % LANE_COUNT;
        uint64_t load = 12ULL * lane + partner_index;
        uint64_t shift = (position % 8ULL) * 8ULL;
        uint64_t injected = ((byte + 1ULL) << shift)
            ^ ((load + 1ULL) * UINT64_C(0x0001000100010001));
        uint64_t xored = lanes[lane] ^ injected;
        uint64_t mixed = xored + initial[(lane + byte) % LANE_COUNT] + position + load;
        lanes[lane] = rotl64(mixed, (unsigned int)(((byte ^ load ^ lane) % 63ULL) + 1ULL));
        position += 1ULL;
        if (position % TOTAL_CAPACITY == 0ULL) {
            round_lanes(lanes, position, q_mixes, q_sums);
        }
    }
    Py_END_ALLOW_THREADS
    PyBuffer_Release(&view);

    PyObject *lane_list = PyList_New(LANE_COUNT);
    if (lane_list == NULL) return NULL;
    for (Py_ssize_t i = 0; i < LANE_COUNT; ++i) {
        PyObject *value = PyLong_FromUnsignedLongLong((unsigned long long)lanes[i]);
        if (value == NULL) {
            Py_DECREF(lane_list);
            return NULL;
        }
        PyList_SET_ITEM(lane_list, i, value);
    }
    PyObject *position_result = PyLong_FromUnsignedLongLong((unsigned long long)position);
    if (position_result == NULL) {
        Py_DECREF(lane_list);
        return NULL;
    }
    PyObject *result = PyTuple_Pack(2, lane_list, position_result);
    Py_DECREF(lane_list);
    Py_DECREF(position_result);
    return result;
}


static inline void absorb_bytes_raw(
    uint64_t lanes[LANE_COUNT],
    uint64_t *position,
    const unsigned char *data,
    Py_ssize_t length,
    const uint64_t initial[LANE_COUNT],
    const uint64_t q_mixes[LANE_COUNT],
    const uint64_t q_sums[LANE_COUNT]
) {
    for (Py_ssize_t offset = 0; offset < length; ++offset) {
        uint64_t byte = (uint64_t)data[offset];
        uint64_t lane = *position % LANE_COUNT;
        uint64_t partner_index = (byte + *position) % LANE_COUNT;
        uint64_t load = 12ULL * lane + partner_index;
        uint64_t shift = (*position % 8ULL) * 8ULL;
        uint64_t injected = ((byte + 1ULL) << shift)
            ^ ((load + 1ULL) * UINT64_C(0x0001000100010001));
        uint64_t mixed = (lanes[lane] ^ injected)
            + initial[(lane + byte) % LANE_COUNT]
            + *position
            + load;
        lanes[lane] = rotl64(mixed, (unsigned int)(((byte ^ load ^ lane) % 63ULL) + 1ULL));
        *position += 1ULL;
        if (*position % TOTAL_CAPACITY == 0ULL) {
            round_lanes(lanes, *position, q_mixes, q_sums);
        }
    }
}

static void store_u64_be(unsigned char out[8], uint64_t value) {
    out[0] = (unsigned char)(value >> 56);
    out[1] = (unsigned char)(value >> 48);
    out[2] = (unsigned char)(value >> 40);
    out[3] = (unsigned char)(value >> 32);
    out[4] = (unsigned char)(value >> 24);
    out[5] = (unsigned char)(value >> 16);
    out[6] = (unsigned char)(value >> 8);
    out[7] = (unsigned char)value;
}

static PyObject *py_finalize_squeeze(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *lanes_obj = NULL;
    PyObject *position_obj = NULL;
    PyObject *initial_obj = NULL;
    PyObject *q_mixes_obj = NULL;
    PyObject *q_sums_obj = NULL;
    PyObject *golden_obj = NULL;
    PyObject *governor_obj = NULL;
    PyObject *closure_obj = NULL;
    Py_ssize_t output_length = 0;

    if (!PyArg_ParseTuple(
            args, "OOOOOOOOn:finalize_squeeze",
            &lanes_obj,
            &position_obj,
            &initial_obj,
            &q_mixes_obj,
            &q_sums_obj,
            &golden_obj,
            &governor_obj,
            &closure_obj,
            &output_length)) {
        return NULL;
    }
    if (output_length < 1) {
        PyErr_SetString(PyExc_ValueError, "output_length must be positive");
        return NULL;
    }

    uint64_t lanes[LANE_COUNT], initial[LANE_COUNT], q_mixes[LANE_COUNT], q_sums[LANE_COUNT];
    if (read_u64_sequence(lanes_obj, lanes, "lanes") < 0
            || read_u64_sequence(initial_obj, initial, "initial_lanes") < 0
            || read_u64_sequence(q_mixes_obj, q_mixes, "q_mixes") < 0
            || read_u64_sequence(q_sums_obj, q_sums, "q_sums") < 0) {
        return NULL;
    }

    uint64_t position = (uint64_t)PyLong_AsUnsignedLongLong(position_obj);
    if (PyErr_Occurred()) return NULL;
    uint64_t golden = (uint64_t)PyLong_AsUnsignedLongLongMask(golden_obj);
    if (PyErr_Occurred()) return NULL;
    uint64_t governor = (uint64_t)PyLong_AsUnsignedLongLongMask(governor_obj);
    if (PyErr_Occurred()) return NULL;

    Py_buffer closure;
    if (PyObject_GetBuffer(closure_obj, &closure, PyBUF_CONTIG_RO) < 0) return NULL;

    PyObject *result = PyBytes_FromStringAndSize(NULL, output_length);
    if (result == NULL) {
        PyBuffer_Release(&closure);
        return NULL;
    }
    unsigned char *out = (unsigned char *)PyBytes_AS_STRING(result);

    uint64_t original_position = position;
    uint64_t bit_len = original_position * 8ULL;
    unsigned char bit_len_bytes[16] = {0};
    store_u64_be(bit_len_bytes + 8, bit_len);

    Py_BEGIN_ALLOW_THREADS
    absorb_bytes_raw(
        lanes,
        &position,
        (const unsigned char *)closure.buf,
        closure.len,
        initial,
        q_mixes,
        q_sums
    );
    absorb_bytes_raw(lanes, &position, bit_len_bytes, 16, initial, q_mixes, q_sums);

    uint64_t final_rounds = 12ULL + (original_position % 12ULL);
    for (uint64_t marker = 0; marker < final_rounds; ++marker) {
        round_lanes(lanes, bit_len + marker + TOTAL_CAPACITY, q_mixes, q_sums);
    }

    Py_ssize_t produced = 0;
    uint64_t block_index = 0;
    while (produced < output_length) {
        for (uint64_t turn = 0; turn < 12ULL; ++turn) {
            uint64_t lane = (block_index + turn) % 12ULL;
            uint64_t counter = ((block_index + 1ULL) * golden)
                ^ ((turn + 1ULL) * governor)
                ^ bit_len
                ^ initial[turn];
            lanes[lane] ^= rotl64(counter, (unsigned int)(((lane + turn + block_index) % 63ULL) + 1ULL));
            round_lanes(
                lanes,
                bit_len + TOTAL_CAPACITY + block_index * 12ULL + turn,
                q_mixes,
                q_sums
            );
        }

        uint64_t words[4];
        for (uint64_t q = 0; q < 4ULL; ++q) {
            uint64_t a = q;
            uint64_t b = q + 4ULL;
            uint64_t c = q + 8ULL;
            uint64_t word = lanes[a]
                + rotl64(lanes[b], (unsigned int)(((q + block_index + 1ULL) % 63ULL) + 1ULL))
                + rotl64(lanes[c], (unsigned int)(((q + block_index + 17ULL) % 63ULL) + 1ULL))
                + q_mixes[a]
                + q_mixes[b]
                + q_mixes[c]
                + ((block_index + 1ULL) * governor);
            word ^= rotl64(lanes[(a + 5ULL) % 12ULL], (unsigned int)(((q + 29ULL) % 63ULL) + 1ULL));
            word = rotl64(word, (unsigned int)(((q * 13ULL + block_index + 1ULL) % 63ULL) + 1ULL));
            words[q] = word;

            unsigned char bytes[8];
            store_u64_be(bytes, word);
            Py_ssize_t take = output_length - produced;
            if (take > 8) take = 8;
            for (Py_ssize_t i = 0; i < take; ++i) out[produced + i] = bytes[i];
            produced += take;
        }

        if (produced >= output_length) break;

        for (uint64_t q = 0; q < 4ULL; ++q) {
            uint64_t word = words[q];
            for (uint64_t offset = 0; offset < 3ULL; ++offset) {
                uint64_t lane = q + offset * 4ULL;
                lanes[lane] = rotl64(
                    lanes[lane] + word + initial[(lane + block_index) % 12ULL],
                    (unsigned int)(((lane + q + block_index + 1ULL) % 63ULL) + 1ULL)
                );
            }
        }
        round_lanes(
            lanes,
            bit_len + TOTAL_CAPACITY + block_index * 12ULL + 12ULL,
            q_mixes,
            q_sums
        );
        block_index += 1ULL;
    }
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&closure);
    return result;
}

static PyMethodDef methods[] = {
    {"absorb_raw", py_absorb_raw, METH_VARARGS, "Absorb bytes through the exact 12-lane ALQC kernel."},
    {"finalize_squeeze", py_finalize_squeeze, METH_VARARGS, "Finalize and squeeze exact ALQC bytes in the compiled kernel."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_alqc_kernel",
    "Compiled ALQC sponge absorption kernel.",
    -1,
    methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit__alqc_kernel(void) {
    return PyModule_Create(&module);
}

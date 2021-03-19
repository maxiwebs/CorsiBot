import numpy as np
import csv
from shapely.geometry import LineString

# for presentations
protocol = [[1,'G'],
[2,'HG'],
[3,'FG'],
[4,'BGD'],
[5,'CGD'],
[6,'EDFG'],
[7,'AFGH'],
[8,'GEABC'],
[9,'CHBDCE'],
[10,'DAFGHEB']]

box_positions = {
        "A": (0.85, 1.0),
        "B": (1.2, 3.6),
        "C": (1.7, 5.1),
        "D": (1.75, 1.4),
        "E": (2.3, 3.9),
        "F": (3.0, 5.2),
        "G": (3.2, 0.8),
        "H": (4.0, 2.0),
        "I": (3.45, 3.25)
}

def complete_dict(d, is_column = True):
    for i in range(1,5+1 if is_column else 4+1):
        if i not in d:
            d[i] = 0
    return d


def number_per_column(sequence):
    columns = [ box_positions[b][1] for b in sequence]
    return complete_dict({x:columns.count(x) for x in columns})

def number_per_row(sequence):
    rows = [ box_positions[b][0] for b in sequence]
    return complete_dict({x:rows.count(x) for x in rows}, is_column=False)


def leftness(sequence):
    columns = number_per_column(sequence)

    ret = 0
    multipliers = [ -2, -1, 0, 1, 2]
    for i in range(1,5+1):
        ret += columns[i] * multipliers[i-1]

    return ret

def frontness(sequence):
    rows = number_per_row(sequence)

    ret = 0
    multipliers = [ 2, 1, -1, -2]
    for i in range(1,4+1):
        ret += rows[i] * multipliers[i-1]

    return ret


def distances(sequence):
    d = []
    for i in range(len(sequence)-1):
        a = box_positions[sequence[i]]
        b = box_positions[sequence[i+1]]
        d.append(np.linalg.norm(np.array(a)-np.array(b)))

    return d


def all_distances():
    ret = []
    for i in list(box_positions.keys()):
        for j in list(box_positions.keys()):
            if i<j:
                ret.append([i,j, distances([i,j])[0]])

    return ret

def greedy_long_path():
    connected = []
    dist = all_distances()
    used = []

    i = 0

    heaviest = sorted(dist, key=lambda x: x[2], reverse=True)[0]
    connected.append((heaviest[0], heaviest[1]))


    head = heaviest[0]
    tail = heaviest[1]

    used.append(head)
    used.append(tail)

    print(heaviest, used, head, tail)

    while len(used)<len(list(box_positions.keys())):
        tail_sel = sorted([ x for x in dist if (x[0] == tail and x[1] not in used) or (x[1] == tail and x[0] not in used)]
            , key=lambda x: x[2], reverse=True)[0]

        head_sel = sorted([ x for x in dist if (x[0] == head and x[1] not in used) or (x[1] == head and x[0] not in used)]
            , key=lambda x: x[2], reverse=True)[0]

        if tail_sel[2]>head_sel[2]:
            heaviest = tail_sel
            new_tail = heaviest[0] if heaviest[1]==tail else heaviest[1]
            used.append(new_tail)
            connected.append((tail, new_tail))
            tail = new_tail
        else:
            heaviest = head_sel
            new_head = heaviest[0] if heaviest[1]==head else heaviest[1]
            used = [new_head] + used
            connected = [(new_head, head)] + connected
            head = new_head

        print(heaviest, used, head, tail)

        i+=1
        if i >= 30:
            print("bardo")
            break

    print(connected)


def save_protocol_csv(protocol, file_name="test.csv"):
    data = []
    data.append(["Ensayo","Sequencia","leftness","frontness","length","distances", "intersections","overlaps"])
    for [ensayo, sequence] in protocol:
        inter = intersections(sequence)
        data.append([ensayo,
                sequence,
                leftness(sequence),
                frontness(sequence),
                "%.2f"%sum(distances(sequence)),
                inter[0],
                inter[1]])

    with open(file_name, 'w') as fp:
        a = csv.writer(fp, delimiter=';')
        a.writerows(data)

def save_csv(file_name="test.csv"):
    data = []
    data.append(["Grupo", "Nivel","Ensayo","Sequencia","number_per_row","number_per_column","leftness","frontness","length","distances", "intersections","overlaps"])
    for (g,gr) in enumerate(trials_group):
        for [nivel, ensayo, sequence] in gr:
            inter = intersections(sequence)
            data.append([g+1,nivel, ensayo, " - ".join(sequence), number_per_row(sequence), number_per_column(sequence),
                leftness(sequence), frontness(sequence),
                "%.2f"%sum(distances(sequence)), ["%.2f" %x for x in distances(sequence)],
                inter[0],inter[1]])

    with open(file_name, 'w') as fp:
        a = csv.writer(fp, delimiter=';')
        a.writerows(data)


def make_segments(p):
    ret = []

    for i in range(0, len(p)-1):
        ret.append([box_positions[p[i]], box_positions[p[i+1]]])

    return ret

def intersections(path):

    segments = make_segments(path)
    count_intersection = 0
    count_overlap = 0

    for i in range(0, len(segments)-1):
        for j in range(i + 1, len(segments)):
            l1 = LineString(segments[i])
            l2 = LineString(segments[j])
            if l1.intersects(l2):
                inter = l1.intersection(l2)
                if i+1 == j and inter.length:
                    count_overlap += 1
                elif i+1!=j and inter.length:
                    count_overlap += 1
                elif i+1!=j and inter.length == 0.0:
                    count_intersection += 1

    return (count_intersection, count_overlap)

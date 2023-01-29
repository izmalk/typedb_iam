import src.io_controller as io_controller
import src.typedb_iam.db_controller as db_controller
import src.data_generation as data_generation


def load_users(session):
    data = data_generation.load_data()
    users = data['user']
    queries = list()

    for user in users:
        name = user['name']
        email = user['email']
        query = 'insert $p isa person, has name "' + name + '", has email "' + email + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(users), 'users:')
    print("Opening file to write users ...")
    with open("logs/user-queries.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)


def load_user_groups(session):
    data = data_generation.load_data()
    users = data['user']
    user_groups = data['user_group']
    subjects = users + user_groups
    group_membership_count = 0
    group_ownership_count = 0
    queries = list()

    for group in user_groups:
        name = group['name']
        group_types = group['type']
        group_membership_count += len(group['member'])
        group_ownership_count += len(group['owner'])

        if 'business_unit' in group_types:
            group_type = 'business-unit'
        elif 'user_role' in group_types:
            group_type = 'user-role'
        elif 'user_account' in group_types:
            group_type = 'user-account'
        else:
            group_type = 'user-group'

        query = 'insert $g isa ' + group_type + ', has name "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(user_groups), 'user groups:')
    print("Opening file to write user_groups ...")
    with open("logs/user-groups-queries.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for group in user_groups:
        group_name = group['name']

        for subject in subjects:
            if subject['uuid'] in group['member']:
                member_name = subject['name']

                query = ' '.join([
                    'match',
                    '$g isa user-group, has name "' + group_name + '";',
                    '$s isa subject, has name "' + member_name + '";',
                    'insert',
                    '$m (user-group: $g, group-member: $s) isa group-membership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', group_membership_count, 'group memberships:')
    print("Opening file to write user group membership ...")
    with open("logs/group-membership-queries.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for group in user_groups:
        group_name = group['name']

        for subject in subjects:
            if subject['uuid'] in group['owner']:
                owner_name = subject['name']

                query = ' '.join([
                    'match',
                    '$g isa user-group, has name "' + group_name + '";',
                    '$s isa subject, has name "' + owner_name + '";',
                    'insert',
                    '$o (owned-group: $g, group-owner: $s) isa group-ownership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', group_ownership_count, 'group ownerships:')
    print("Opening file to write user group ownership ...")
    with open("logs/group-ownership-queries.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)


def load_subjects(session):
    load_users(session)
    load_user_groups(session)


def load_resources(session):
    data = data_generation.load_data()
    resources = data['resource']
    subjects = data['user'] + data['user_group']
    resource_ownership_count = 0
    queries = list()

    for resource in resources:
        name = resource['name']
        resource_ownership_count += len(resource['owner'])
        query = 'insert $f isa file, has name "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(resources), 'resources:')
    print("Opening file to write resources ...")
    with open("logs/resources.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for resource in resources:
        resource_name = resource['name']

        for subject in subjects:
            if subject['uuid'] in resource['owner']:
                owner_name = subject['name']

                query = ' '.join([
                    'match',
                    '$r isa resource, has name "' + resource_name + '";',
                    '$s isa subject, has name "' + owner_name + '";',
                    'insert',
                    '$o (owned-object: $r, object-owner: $s) isa object-ownership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', resource_ownership_count, 'resource ownerships:')
    print("Opening file to write resource ownership ...")
    with open("logs/resource-ownership.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)


def load_resource_collections(session):
    data = data_generation.load_data()
    resources = data['resource']
    resource_collections = data['resource_collection']
    objects = resources + resource_collections
    subjects = data['user'] + data['user_group']
    collection_membership_count = 0
    collection_ownership_count = 0
    queries = list()

    for collection in resource_collections:
        name = collection['name']
        collection_membership_count += len(collection['member'])
        collection_ownership_count += len(collection['owner'])
        query = 'insert $d isa directory, has name "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(resource_collections), 'resource collections:')
    print("Opening file to write resource collections ...")
    with open("logs/collections.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for collection in resource_collections:
        collection_name = collection['name']

        for obj in objects:
            if obj['uuid'] in collection['member']:
                member_name = obj['name']

                query = ' '.join([
                    'match',
                    '$c isa resource-collection, has name "' + collection_name + '";',
                    '$o isa object, has name "' + member_name + '";',
                    'insert',
                    '$m (resource-collection: $c, collection-member: $o) isa collection-membership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', collection_membership_count, 'collection memberships:')
    print("Opening file to write collections membership ...")
    with open("logs/collection-membership.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for collection in resource_collections:
        collection_name = collection['name']

        for subject in subjects:
            if subject['uuid'] in collection['owner']:
                owner_name = subject['name']

                query = ' '.join([
                    'match',
                    '$c isa resource-collection, has name "' + collection_name + '";',
                    '$s isa subject, has name "' + owner_name + '";',
                    'insert',
                    '$o (owned-object: $c, object-owner: $s) isa object-ownership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', collection_ownership_count, 'collection ownerships:')
    print("Opening file to write collection ownership ...")
    with open("logs/collection-ownership.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)


def load_objects(session):
    load_resources(session)
    load_resource_collections(session)


def load_operations(session):
    data = data_generation.load_data()
    operations = data['operation']
    objects = data['resource'] + data['resource_collection']
    queries = list()

    for operation in operations:
        name = operation['name']
        query = 'insert $o isa operation, has name "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(operations), 'operations:')
    print("Opening file to write operations ...")
    with open("logs/operations.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for operation in operations:
        operation_name = operation['name']

        for obj in objects:
            object_types = list(object_type for object_type in obj['type'] if object_type in operation['object_type'])

            if len(object_types) != 0:
                object_name = obj['name']
                object_type = object_types[0]

                query = ' '.join([
                    'match',
                    '$ob isa ' + object_type.replace('_', '-') + ', has name "' + object_name + '";',
                    '$op isa operation, has name "' + operation_name + '";',
                    'insert',
                    '$a (accessed-object: $ob, valid-action: $op) isa access;'
                ])

                queries.append(query)

    io_controller.out_info('Loading up to', len(operations) * len(objects), 'potential accesses:')
    print("Opening file to write potential accesses ...")
    with open("logs/potential-accesses.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)


def load_operation_sets(session):
    data = data_generation.load_data()
    operations = data['operation']
    operation_sets = data['operation_set']
    actions = operations + operation_sets
    objects = data['resource'] + data['resource_collection']
    set_membership_count = 0
    queries = list()

    for opset in operation_sets:
        name = opset['name']
        set_membership_count += len(opset['member'])
        query = 'insert $s isa operation-set, has name "' + name + '";'
        queries.append(query)

    io_controller.out_info('Loading', len(operation_sets), 'operation sets:')
    print("Opening file to write operation sets ...")
    with open("logs/operation-sets.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for opset in operation_sets:
        set_name = opset['name']

        for action in actions:
            if action['uuid'] in opset['member']:
                member_name = action['name']

                query = ' '.join([
                    'match',
                    '$s isa operation-set, has name "' + set_name + '";',
                    '$a isa action, has name "' + member_name + '";',
                    'insert'
                    '$m (operation-set: $s, set-member: $a) isa set-membership;'
                ])

                queries.append(query)

    io_controller.out_info('Loading', set_membership_count, 'set memberships:')
    print("Opening file to write set membership ...")
    with open("logs/set-membership.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)
    queries = list()

    for opset in operation_sets:
        set_name = opset['name']

        for obj in objects:
            object_types = list(object_type for object_type in obj['type'] if object_type in opset['object_type'])

            if len(object_types) != 0:
                object_name = obj['name']
                object_type = object_types[0]

                query = ' '.join([
                    'match',
                    '$o isa ' + object_type.replace('_', '-') + ', has name "' + object_name + '";',
                    '$s isa operation-set, has name "' + set_name + '";',
                    'insert',
                    '$a (accessed-object: $o, valid-action: $s) isa access;'
                ])

                queries.append(query)

    io_controller.out_info('Loading up to', len(operation_sets) * len(objects), 'potential accesses:')
    print("Opening file to write potential accesses for sets ...")
    with open("logs/potential-accesses-for-sets.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)


def load_actions(session):
    load_operations(session)
    load_operation_sets(session)


def load_permissions(session):
    data = data_generation.load_data()
    permissions = data['permission']
    subjects = data['user'] + data['user_group']
    objects = data['resource'] + data['resource_collection']
    actions = data['operation'] + data['operation_set']
    queries = list()

    for permission in permissions:
        subject_type = permission['subject_type']
        object_type = permission['object_type']

        for subject in subjects:
            if subject['uuid'] in permission['subject']:
                for obj in objects:
                    if obj['uuid'] in permission['object']:
                        for action in actions:
                            if action['uuid'] in permission['action']:
                                subject_name = subject['name']
                                object_name = obj['name']
                                action_name = action['name']

                                query = ' '.join([
                                    'match',
                                    '$s isa ' + subject_type.replace('_', '-') + ', has name "' + subject_name + '";',
                                    '$o isa ' + object_type.replace('_', '-') + ', has name "' + object_name + '";',
                                    '$a isa action, has name "' + action_name + '";',
                                    '$ac (accessed-object: $o, valid-action: $a) isa access;',
                                    'insert',
                                    '$p (permitted-subject: $s, permitted-access: $ac) isa permission;'
                                ])

                                queries.append(query)

    io_controller.out_info('Loading', len(permissions), 'permissions:')
    print("Opening file to write permissions ...")
    with open("logs/permissions.txt", "a") as file:
        for query in queries:
            file.write(query + "\n")
    db_controller.insert(session, queries, display_progress=True)


def load_data(session):
    load_subjects(session)
    load_objects(session)
    load_actions(session)
    load_permissions(session)
